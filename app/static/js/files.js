/**
 * My Files Management Controller
 * Handles live search, multi-criteria filtering, sorting, secure download, and reference deletion.
 */

let currentPage = 1;
let currentSortOrder = 'desc';
let searchDebounceTimer = null;

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchInput');
  const typeFilter = document.getElementById('typeFilter');
  const statusFilter = document.getElementById('statusFilter');
  const sortBy = document.getElementById('sortBy');
  const sortOrderBtn = document.getElementById('sortOrderBtn');
  const resetBtn = document.getElementById('resetFiltersBtn');

  // Debounced search
  searchInput.addEventListener('input', () => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      currentPage = 1;
      fetchAndRenderFiles();
    }, 300);
  });

  typeFilter.addEventListener('change', () => {
    currentPage = 1;
    fetchAndRenderFiles();
  });

  statusFilter.addEventListener('change', () => {
    currentPage = 1;
    fetchAndRenderFiles();
  });

  sortBy.addEventListener('change', () => {
    currentPage = 1;
    fetchAndRenderFiles();
  });

  sortOrderBtn.addEventListener('click', () => {
    currentSortOrder = (currentSortOrder === 'asc') ? 'desc' : 'asc';
    document.getElementById('sortOrderText').textContent = currentSortOrder.toUpperCase();
    document.getElementById('sortOrderIcon').className =
      currentSortOrder === 'asc' ? 'bi bi-sort-up' : 'bi bi-sort-down';
    fetchAndRenderFiles();
  });

  resetBtn.addEventListener('click', () => {
    searchInput.value = '';
    typeFilter.value = '';
    statusFilter.value = '';
    sortBy.value = 'date';
    currentSortOrder = 'desc';
    document.getElementById('sortOrderText').textContent = 'DESC';
    document.getElementById('sortOrderIcon').className = 'bi bi-sort-down';
    currentPage = 1;
    fetchAndRenderFiles();
  });

  // Initial load
  fetchAndRenderFiles();
});

async function fetchAndRenderFiles() {
  const search = document.getElementById('searchInput').value.trim();
  const fileType = document.getElementById('typeFilter').value;
  const status = document.getElementById('statusFilter').value;
  const sortBy = document.getElementById('sortBy').value;

  const queryParams = new URLSearchParams({
    search: search,
    type: fileType,
    status: status,
    sort: sortBy,
    order: currentSortOrder,
    page: currentPage,
    per_page: 15,
  });

  const tbody = document.getElementById('filesTableBody');
  tbody.innerHTML = `
    <tr>
      <td colspan="6" class="text-center py-4 text-muted">
        <div class="spinner-border spinner-border-sm text-primary me-2"></div> Loading files...
      </td>
    </tr>
  `;

  const res = await apiRequest(`/api/files?${queryParams.toString()}`);
  if (!res.ok) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="text-center py-4 text-danger">
          <i class="bi bi-exclamation-triangle me-2"></i> Failed to load files: ${res.data.error || 'Server error'}
        </td>
      </tr>
    `;
    return;
  }

  const { files, total_items, total_pages, page } = res.data;

  if (!files || files.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="text-center py-5">
          <div class="text-muted mb-2"><i class="bi bi-folder2 fs-1"></i></div>
          <h6 class="fw-semibold text-secondary">No files found</h6>
          <p class="small text-muted mb-3">No file references matched your active query filters.</p>
          <a href="/upload" class="btn btn-outline-primary btn-sm rounded-3">Upload a File</a>
        </td>
      </tr>
    `;
    updatePaginationUI(0, 1, 1);
    return;
  }

  tbody.innerHTML = files.map(file => `
    <tr>
      <td>
        <div class="d-flex align-items-center gap-2">
          <i class="bi ${file.icon_class} fs-4"></i>
          <div>
            <div class="fw-semibold text-dark">${escapeHtml(file.display_name)}</div>
            <span class="badge bg-light text-muted fw-normal" style="font-size: 0.75rem;">${file.category}</span>
          </div>
        </div>
      </td>
      <td class="fw-medium">${file.formatted_size}</td>
      <td>
        ${file.is_duplicate
          ? '<span class="badge-duplicate"><i class="bi bi-intersect me-1"></i>Duplicate</span>'
          : '<span class="badge-original"><i class="bi bi-check-circle me-1"></i>Original</span>'
        }
      </td>
      <td>
        <span class="hash-badge" title="${file.sha256_hash}">
          ${file.short_hash}
        </span>
      </td>
      <td class="text-muted small">${file.uploaded_at}</td>
      <td class="text-end">
        <div class="btn-group btn-group-sm">
          <button type="button" class="btn btn-outline-primary" onclick="downloadFile(${file.id}, '${escapeQuotes(file.display_name)}')" title="Download File">
            <i class="bi bi-download"></i>
          </button>
          <button type="button" class="btn btn-outline-danger" onclick="deleteFileReference(${file.id}, '${escapeQuotes(file.display_name)}')" title="Delete Reference">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');

  updatePaginationUI(total_items, page, total_pages);
}

function updatePaginationUI(totalItems, page, totalPages) {
  const infoEl = document.getElementById('paginationInfo');
  const navEl = document.getElementById('paginationNav');

  infoEl.textContent = `Showing page ${page} of ${totalPages} (${totalItems} total references)`;

  if (totalPages <= 1) {
    navEl.innerHTML = '';
    return;
  }

  let html = '';
  html += `
    <li class="page-item ${page <= 1 ? 'disabled' : ''}">
      <a class="page-link" href="javascript:void(0);" onclick="goToPage(${page - 1})">Previous</a>
    </li>
  `;

  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= page - 1 && i <= page + 1)) {
      html += `
        <li class="page-item ${i === page ? 'active' : ''}">
          <a class="page-link" href="javascript:void(0);" onclick="goToPage(${i})">${i}</a>
        </li>
      `;
    } else if (i === page - 2 || i === page + 2) {
      html += `<li class="page-item disabled"><span class="page-link">&hellip;</span></li>`;
    }
  }

  html += `
    <li class="page-item ${page >= totalPages ? 'disabled' : ''}">
      <a class="page-link" href="javascript:void(0);" onclick="goToPage(${page + 1})">Next</a>
    </li>
  `;

  navEl.innerHTML = html;
}

function goToPage(page) {
  currentPage = page;
  fetchAndRenderFiles();
}

// Secure Download File Trigger
async function downloadFile(fileId, filename) {
  const token = await getAuthToken();
  if (!token) {
    showToast('Unauthorized', 'Please sign in to download files.', 'danger');
    return;
  }

  showToast('Preparing Download', `Retrieving '${filename}' from cloud storage...`, 'info');

  try {
    const response = await fetch(`/api/files/${fileId}/download`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Download failed' }));
      showToast('Download Error', err.error || 'Failed to download file.', 'danger');
      return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();

    showToast('Download Complete', `'${filename}' downloaded successfully.`, 'success');
  } catch (err) {
    console.error("Download exception:", err);
    showToast('Download Error', err.message || 'Error downloading file.', 'danger');
  }
}

// Delete Reference Confirmation
function deleteFileReference(fileId, filename) {
  showConfirmModal(
    'Delete File Reference',
    `Are you sure you want to delete '${filename}'? If no other user or reference links to this underlying content, it will also be purged from Firebase Cloud Storage.`,
    async () => {
      const res = await apiRequest(`/api/files/${fileId}`, {
        method: 'DELETE',
      });

      if (res.ok && res.data.success) {
        showToast('File Deleted', res.data.message, 'success');
        fetchAndRenderFiles();
      } else {
        showToast('Delete Failed', res.data.error || 'Could not delete file reference.', 'danger');
      }
    }
  );
}

function escapeQuotes(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
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
