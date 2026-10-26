/**
 * Storage Statistics Controller
 * Renders detailed analytical charts, formula verification, largest objects, and savings leaderboards.
 */

let categoryChart = null;
let trendChart = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadStatisticsData();
});

async function loadStatisticsData() {
  const [summaryRes, fileTypesRes, trendsRes, largestRes, dupRes] = await Promise.all([
    apiRequest('/api/statistics/summary'),
    apiRequest('/api/statistics/file-types'),
    apiRequest('/api/statistics/trends'),
    apiRequest('/api/statistics/largest-files'),
    apiRequest('/api/duplicates'),
  ]);

  if (!summaryRes.ok) {
    console.error("Failed to load statistics summary:", summaryRes.data.error);
    return;
  }

  const { metrics } = summaryRes.data;

  // 1. Populate Metrics & Formulas
  document.getElementById('statsTotalRefs').textContent = metrics.total_files.toLocaleString();
  document.getElementById('statsUniqueObjects').textContent = metrics.unique_files.toLocaleString();
  document.getElementById('statsSavedBytes').textContent = metrics.saved_formatted;
  document.getElementById('statsSavingPercent').textContent = `${metrics.saving_percentage}%`;

  document.getElementById('statsLogicalStorage').textContent = metrics.logical_formatted;
  document.getElementById('statsPhysicalStorage').textContent = metrics.physical_formatted;
  document.getElementById('statsPreservedStorage').textContent = metrics.saved_formatted;

  // 2. Render Category Volume Chart
  if (fileTypesRes.ok && fileTypesRes.data.file_types) {
    renderCategoryVolumeChart(fileTypesRes.data.file_types);
  }

  // 3. Render Trend Line Chart
  if (trendsRes.ok && trendsRes.data.trends) {
    renderDetailedTrendChart(trendsRes.data.trends);
  }

  // 4. Populate Largest Files Table
  if (largestRes.ok && largestRes.data.largest_files) {
    renderLargestFilesTable(largestRes.data.largest_files);
  }

  // 5. Populate Top Duplicate Groups Table
  if (dupRes.ok && dupRes.data.duplicate_groups) {
    renderTopDuplicateGroupsTable(dupRes.data.duplicate_groups);
  }
}

function renderCategoryVolumeChart(fileTypes) {
  const ctx = document.getElementById('categoryVolumeChart');
  if (!ctx) return;

  if (categoryChart) categoryChart.destroy();

  const labels = fileTypes.labels.length > 0 ? fileTypes.labels : ['No Categories'];
  const sizesMB = fileTypes.sizes_bytes.map(b => (b / (1024 * 1024)).toFixed(2));

  categoryChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Logical Storage (MB)',
        data: sizesMB.length > 0 ? sizesMB : [0],
        backgroundColor: '#0ea5e9',
        borderRadius: 6,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.raw} MB`
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          title: { display: true, text: 'Megabytes (MB)' },
          grid: { color: 'rgba(0,0,0,0.05)' }
        },
        y: { grid: { display: false } }
      }
    }
  });
}

function renderDetailedTrendChart(trends) {
  const ctx = document.getElementById('detailedTrendChart');
  if (!ctx) return;

  if (trendChart) trendChart.destroy();

  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: trends.labels.map(l => l.slice(5)),
      datasets: [
        {
          label: 'New Physical Files',
          data: trends.new_uploads,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 2,
        },
        {
          label: 'Duplicates Detected',
          data: trends.duplicate_detected,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 2,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 },
          title: { display: true, text: 'Event Count' },
          grid: { color: 'rgba(0,0,0,0.05)' }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderLargestFilesTable(largestFiles) {
  const tbody = document.getElementById('largestFilesTableBody');
  if (!tbody) return;

  if (!largestFiles || largestFiles.length === 0) {
    tbody.innerHTML = `<tr><td colspan="3" class="text-center py-4 text-muted small">No files uploaded yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = largestFiles.map(file => `
    <tr>
      <td>
        <div class="d-flex align-items-center gap-2">
          <i class="bi ${file.icon_class} fs-5"></i>
          <div>
            <div class="fw-semibold text-dark small">${escapeHtml(file.display_name)}</div>
            <span class="text-muted" style="font-size: 0.725rem;">${file.category}</span>
          </div>
        </div>
      </td>
      <td class="fw-semibold small">${file.formatted_size}</td>
      <td>
        <span class="hash-badge" style="font-size: 0.75rem;">${file.short_hash}</span>
      </td>
    </tr>
  `).join('');
}

function renderTopDuplicateGroupsTable(groups) {
  const tbody = document.getElementById('topGroupsTableBody');
  if (!tbody) return;

  if (!groups || groups.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-muted small">No duplicate clusters found.</td></tr>`;
    return;
  }

  // Show top 5 groups with highest savings
  const topGroups = groups.slice(0, 5);
  tbody.innerHTML = topGroups.map(g => `
    <tr>
      <td>
        <div class="d-flex align-items-center gap-2">
          <i class="bi ${g.icon_class} fs-5"></i>
          <div>
            <div class="fw-semibold text-dark small">${escapeHtml(g.original_filename)}</div>
            <span class="text-muted" style="font-size: 0.725rem;">Group #${g.group_id}</span>
          </div>
        </div>
      </td>
      <td class="small fw-medium">${g.reference_count}</td>
      <td class="small fw-bold text-success">${g.formatted_savings}</td>
      <td class="text-end">
        <a href="/duplicate-groups/${g.group_id}" class="btn btn-outline-primary btn-sm py-0 px-2" style="font-size: 0.75rem;">
          View
        </a>
      </td>
    </tr>
  `).join('');
}

function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
