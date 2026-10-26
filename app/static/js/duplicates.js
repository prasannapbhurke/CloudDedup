/**
 * Duplicate Groups Controller
 * Manages overview cards for groups with >= 2 references, and the deep inspection details page.
 */

document.addEventListener('DOMContentLoaded', () => {
  if (typeof CURRENT_GROUP_ID !== 'undefined') {
    loadGroupDetails(CURRENT_GROUP_ID);
  } else if (document.getElementById('duplicateGroupsContainer')) {
    loadDuplicateGroups();
  }
});

// -------------------------------------------------------------
// Overview Page: Load All Duplicate Groups
// -------------------------------------------------------------
async function loadDuplicateGroups() {
  const container = document.getElementById('duplicateGroupsContainer');
  if (!container) return;

  const res = await apiRequest('/api/duplicates');
  if (!res.ok) {
    container.innerHTML = `
      <div class="col-12 text-center py-5 text-danger">
        <i class="bi bi-exclamation-triangle fs-1"></i>
        <h6 class="mt-2">Failed to load duplicate groups: ${res.data.error || 'Server error'}</h6>
      </div>
    `;
    return;
  }

  const { duplicate_groups } = res.data;

  if (!duplicate_groups || duplicate_groups.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center py-5">
        <div class="text-muted mb-2"><i class="bi bi-intersect fs-1"></i></div>
        <h5 class="fw-semibold text-secondary">No Duplicate Groups Detected</h5>
        <p class="small text-muted mb-3 max-w-500 mx-auto">
          You haven't uploaded identical files yet. When you upload two or more files with the same content (even under different names), they will cluster here.
        </p>
        <a href="/upload" class="btn btn-outline-primary btn-sm rounded-3">Upload Duplicate Test Files</a>
      </div>
    `;
    return;
  }

  container.innerHTML = duplicate_groups.map(group => `
    <div class="col-lg-6 col-xl-4">
      <div class="card border-0 shadow-sm rounded-4 p-4 h-100 bg-white d-flex flex-column justify-content-between">
        <div>
          <div class="d-flex justify-content-between align-items-start mb-3">
            <div class="d-flex align-items-center gap-2">
              <i class="bi ${group.icon_class} fs-3"></i>
              <div>
                <h6 class="fw-bold mb-0 text-dark">${escapeHtml(group.original_filename)}</h6>
                <span class="badge bg-light text-muted fw-normal" style="font-size: 0.75rem;">Group #${group.group_id}</span>
              </div>
            </div>
            <span class="badge bg-warning-subtle text-warning border border-warning-subtle py-1 px-2 rounded-pill small">
              ${group.reference_count} References
            </span>
          </div>

          <div class="bg-light p-3 rounded-3 mb-3 border">
            <div class="d-flex justify-content-between small text-muted mb-1">
              <span>Physical File Size:</span>
              <strong class="text-dark">${group.formatted_size}</strong>
            </div>
            <div class="d-flex justify-content-between small text-muted mb-1">
              <span>SHA-256 Fingerprint:</span>
              <span class="hash-badge" title="${group.sha256_hash}">${group.short_hash}</span>
            </div>
            <div class="d-flex justify-content-between small text-muted">
              <span>Cloud Storage Saved:</span>
              <strong class="text-success">${group.formatted_savings}</strong>
            </div>
          </div>
        </div>

        <a href="/duplicate-groups/${group.group_id}" class="btn btn-outline-primary btn-sm w-100 rounded-3 py-2 d-flex align-items-center justify-content-center gap-1">
          <span>View Group References</span>
          <i class="bi bi-arrow-right"></i>
        </a>
      </div>
    </div>
  `).join('');
}

// -------------------------------------------------------------
// Details Page: Load References Inside Specific Duplicate Group
// -------------------------------------------------------------
async function loadGroupDetails(groupId) {
  const res = await apiRequest(`/api/duplicates/${groupId}`);
  if (!res.ok) {
    showToast('Group Unavailable', res.data.error || 'Group not found or has fewer than 2 references.', 'warning');
    setTimeout(() => {
      window.location.href = '/duplicate-groups';
    }, 1500);
    return;
  }

  const { group } = res.data;

  // Header stats
  document.getElementById('groupFullHash').textContent = group.sha256_hash;
  document.getElementById('groupFullHash').title = group.sha256_hash;
  document.getElementById('groupPhysicalSize').textContent = group.formatted_size;
  document.getElementById('groupRefCount').textContent = `${group.reference_count} file references`;
  document.getElementById('groupSavedBytes').textContent = `${group.formatted_savings} (${group.formatted_size} × [${group.reference_count} - 1])`;

  // References table
  const tbody = document.getElementById('groupReferencesTableBody');
  tbody.innerHTML = group.references.map(ref => `
    <tr>
      <td>
        <div class="d-flex align-items-center gap-2">
          <i class="bi ${ref.icon_class} fs-4"></i>
          <div>
            <div class="fw-semibold text-dark">${escapeHtml(ref.display_name)}</div>
            <span class="badge bg-light text-muted fw-normal" style="font-size: 0.75rem;">${ref.category}</span>
          </div>
        </div>
      </td>
      <td class="fw-medium">${ref.formatted_size}</td>
      <td>
        ${ref.is_duplicate
          ? '<span class="badge-duplicate"><i class="bi bi-intersect me-1"></i>Duplicate Reference</span>'
          : '<span class="badge-original"><i class="bi bi-check-circle me-1"></i>Earliest Reference</span>'
        }
      </td>
      <td class="text-muted small">${ref.uploaded_at}</td>
      <td class="text-end">
        <div class="btn-group btn-group-sm">
          <button type="button" class="btn btn-outline-primary" onclick="downloadFile(${ref.id}, '${escapeQuotes(ref.display_name)}')" title="Download">
            <i class="bi bi-download"></i>
          </button>
          <button type="button" class="btn btn-outline-danger" onclick="deleteGroupReference(${ref.id}, '${escapeQuotes(ref.display_name)}', ${groupId})" title="Delete Reference">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

// Group Reference Deletion Handler
function deleteGroupReference(refId, filename, groupId) {
  showConfirmModal(
    'Delete Duplicate Reference',
    `Are you sure you want to delete '${filename}' from this duplicate group?`,
    async () => {
      const res = await apiRequest(`/api/files/${refId}`, { method: 'DELETE' });
      if (res.ok && res.data.success) {
        showToast('Reference Deleted', res.data.message, 'success');
        // Reload details to check if group still has >= 2 references
        loadGroupDetails(groupId);
      } else {
        showToast('Error', res.data.error || 'Failed to delete reference.', 'danger');
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
