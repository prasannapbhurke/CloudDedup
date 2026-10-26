/**
 * Dashboard Controller
 * Loads live MySQL metrics and initializes Chart.js visualizations.
 */

let storageChart = null;
let ratioChart = null;
let typeChart = null;
let activityChart = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadDashboardData();
});

async function loadDashboardData() {
  const [summaryRes, fileTypesRes, trendsRes] = await Promise.all([
    apiRequest('/api/dashboard/summary'),
    apiRequest('/api/statistics/file-types'),
    apiRequest('/api/statistics/trends'),
  ]);

  if (!summaryRes.ok) {
    console.error("Failed to load dashboard summary:", summaryRes.data.error);
    return;
  }

  const { metrics, recent_uploads } = summaryRes.data;

  // 1. Populate Metric Cards
  document.getElementById('statTotalFiles').textContent = metrics.total_files.toLocaleString();
  document.getElementById('statUniqueFiles').textContent = metrics.unique_files.toLocaleString();
  document.getElementById('statDuplicateRefs').textContent = metrics.duplicate_references.toLocaleString();
  document.getElementById('statSavingPercent').textContent = `${metrics.saving_percentage}%`;

  document.getElementById('statLogicalStorage').textContent = metrics.logical_formatted;
  document.getElementById('statPhysicalStorage').textContent = metrics.physical_formatted;
  document.getElementById('statStorageSaved').textContent = metrics.saved_formatted;

  // 2. Render Chart 1: Logical vs Physical Storage
  renderStorageComparisonChart(metrics.logical_bytes, metrics.physical_bytes);

  // 3. Render Chart 2: Unique Files vs Duplicate References
  renderFilesRatioChart(metrics.unique_files, metrics.duplicate_references);

  // 4. Render Chart 3: File Type Distribution
  if (fileTypesRes.ok && fileTypesRes.data.file_types) {
    renderFileTypeChart(fileTypesRes.data.file_types);
  }

  // 5. Render Chart 4: Upload Activity Over Time
  if (trendsRes.ok && trendsRes.data.trends) {
    renderActivityChart(trendsRes.data.trends);
  }

  // 6. Populate Recent Upload Activity Table
  renderRecentUploadsTable(recent_uploads);
}

// Chart 1: Storage Comparison (MB)
function renderStorageComparisonChart(logicalBytes, physicalBytes) {
  const ctx = document.getElementById('storageComparisonChart');
  if (!ctx) return;

  const logicalMB = (logicalBytes / (1024 * 1024)).toFixed(2);
  const physicalMB = (physicalBytes / (1024 * 1024)).toFixed(2);

  if (storageChart) storageChart.destroy();

  storageChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Logical Storage (Total)', 'Physical Cloud Storage'],
      datasets: [{
        label: 'Storage (MB)',
        data: [logicalMB, physicalMB],
        backgroundColor: ['rgba(59, 130, 246, 0.75)', 'rgba(16, 185, 129, 0.75)'],
        borderColor: ['#2563eb', '#059669'],
        borderWidth: 1.5,
        borderRadius: 8,
      }]
    },
    options: {
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
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Megabytes (MB)' },
          grid: { color: 'rgba(0,0,0,0.05)' }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

// Chart 2: Unique Files vs Duplicate References (Doughnut)
function renderFilesRatioChart(uniqueCount, duplicateCount) {
  const ctx = document.getElementById('filesRatioChart');
  if (!ctx) return;

  if (ratioChart) ratioChart.destroy();

  const total = uniqueCount + duplicateCount;
  const data = total === 0 ? [1] : [uniqueCount, duplicateCount];
  const colors = total === 0 ? ['#e2e8f0'] : ['#3b82f6', '#f59e0b'];
  const labels = total === 0 ? ['No Files Yet'] : ['Unique Files', 'Duplicate References'];

  ratioChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#ffffff',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      },
      cutout: '70%',
    }
  });
}

// Chart 3: File Type Distribution
function renderFileTypeChart(fileTypes) {
  const ctx = document.getElementById('fileTypeChart');
  if (!ctx) return;

  if (typeChart) typeChart.destroy();

  const labels = fileTypes.labels.length > 0 ? fileTypes.labels : ['No Files'];
  const counts = fileTypes.counts.length > 0 ? fileTypes.counts : [1];
  const bgColors = [
    '#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4', '#64748b'
  ];

  typeChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: counts,
        backgroundColor: fileTypes.labels.length > 0 ? bgColors.slice(0, labels.length) : ['#e2e8f0'],
        borderWidth: 2,
        borderColor: '#ffffff',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}

// Chart 4: Upload Activity Over Time (Grouped Bar)
function renderActivityChart(trends) {
  const ctx = document.getElementById('uploadActivityChart');
  if (!ctx) return;

  if (activityChart) activityChart.destroy();

  activityChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: trends.labels.map(l => l.slice(5)), // MM-DD
      datasets: [
        {
          label: 'New Physical Files',
          data: trends.new_uploads,
          backgroundColor: '#3b82f6',
          borderRadius: 4,
        },
        {
          label: 'Duplicates Detected',
          data: trends.duplicate_detected,
          backgroundColor: '#f59e0b',
          borderRadius: 4,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true, grid: { display: false } },
        y: {
          stacked: true,
          beginAtZero: true,
          ticks: { stepSize: 1 },
          title: { display: true, text: 'File Count' },
          grid: { color: 'rgba(0,0,0,0.05)' }
        }
      },
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}

// Populate Recent Uploads Table
function renderRecentUploadsTable(uploads) {
  const tbody = document.getElementById('recentUploadsTableBody');
  if (!tbody) return;

  if (!uploads || uploads.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center py-5">
          <div class="text-muted mb-2"><i class="bi bi-cloud-arrow-up fs-1"></i></div>
          <h6 class="fw-semibold text-secondary">No files uploaded yet</h6>
          <p class="small text-muted mb-3">Upload your first file to test content-based deduplication.</p>
          <a href="/upload" class="btn btn-primary btn-sm rounded-3">Upload Your First File</a>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = uploads.map(item => `
    <tr>
      <td>
        <div class="d-flex align-items-center gap-2">
          <i class="bi ${item.icon_class} fs-4"></i>
          <div>
            <div class="fw-semibold text-dark">${escapeHtml(item.filename)}</div>
            <span class="badge bg-light text-muted fw-normal" style="font-size: 0.75rem;">${item.category}</span>
          </div>
        </div>
      </td>
      <td class="fw-medium">${item.formatted_size}</td>
      <td>
        ${item.is_duplicate
          ? '<span class="badge-duplicate"><i class="bi bi-intersect me-1"></i>Duplicate Content</span>'
          : '<span class="badge-original"><i class="bi bi-check-circle me-1"></i>Original File</span>'
        }
      </td>
      <td>
        <span class="hash-badge" title="${item.sha256_hash}">
          ${item.short_hash}
        </span>
      </td>
      <td class="text-muted small">${item.created_at}</td>
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
