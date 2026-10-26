/**
 * Upload Page Controller
 * Handles Drag & Drop, File Selection, Progress Indication, and Deduplication Result Notification.
 */

let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('uploadDropzone');
  const fileInput = document.getElementById('fileInput');
  const browseBtn = document.getElementById('browseFileBtn');
  const clearBtn = document.getElementById('clearFileBtn');
  const cancelBtn = document.getElementById('cancelBtn');
  const uploadBtn = document.getElementById('uploadBtn');
  const uploadAnotherBtn = document.getElementById('uploadAnotherBtn');

  // Trigger file browser on click
  browseBtn.addEventListener('click', () => fileInput.click());
  dropzone.addEventListener('click', (e) => {
    if (e.target !== browseBtn && !browseBtn.contains(e.target)) {
      fileInput.click();
    }
  });

  // Drag & Drop handlers
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  clearBtn.addEventListener('click', resetSelection);
  cancelBtn.addEventListener('click', resetSelection);

  if (uploadAnotherBtn) {
    uploadAnotherBtn.addEventListener('click', () => {
      document.getElementById('dedupResultCard').classList.add('d-none');
      resetSelection();
    });
  }

  // Upload Button Trigger
  uploadBtn.addEventListener('click', executeUpload);
});

function handleFileSelected(file) {
  selectedFile = file;

  // Update UI Preview
  document.getElementById('previewFilename').textContent = file.name;
  document.getElementById('previewSize').textContent = formatBytesJs(file.size);
  document.getElementById('previewType').textContent = file.type || 'Unknown MIME';

  // Choose icon based on file extension
  const ext = file.name.split('.').pop().toLowerCase();
  const iconEl = document.getElementById('previewIcon');
  iconEl.innerHTML = `<i class="bi ${getIconForExt(ext)}"></i>`;

  document.getElementById('filePreviewCard').classList.remove('d-none');
  document.getElementById('uploadBtn').disabled = false;
  document.getElementById('cancelBtn').disabled = false;
  document.getElementById('dedupResultCard').classList.add('d-none');
}

function resetSelection() {
  selectedFile = null;
  document.getElementById('fileInput').value = '';
  document.getElementById('filePreviewCard').classList.add('d-none');
  document.getElementById('uploadProgressBar').classList.add('d-none');
  document.getElementById('uploadBtn').disabled = true;
  document.getElementById('cancelBtn').disabled = true;
}

async function executeUpload() {
  if (!selectedFile) return;

  const uploadBtn = document.getElementById('uploadBtn');
  const cancelBtn = document.getElementById('cancelBtn');
  const progressBar = document.getElementById('uploadProgressBar');
  const progressBarInner = progressBar.querySelector('.progress-bar');
  const spinner = document.getElementById('uploadBtnSpinner');
  const btnText = document.getElementById('uploadBtnText');

  // Disable buttons & show loading
  uploadBtn.disabled = true;
  cancelBtn.disabled = true;
  progressBar.classList.remove('d-none');
  progressBarInner.style.width = '40%';
  spinner.classList.remove('d-none');
  btnText.textContent = 'Hashing & Verifying...';

  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    progressBarInner.style.width = '75%';
    btnText.textContent = 'Processing Deduplication...';

    const res = await apiRequest('/api/files/upload', {
      method: 'POST',
      body: formData,
    });

    progressBarInner.style.width = '100%';

    if (res.ok && res.data.success) {
      const data = res.data;
      displayDeduplicationResult(data);
      resetSelection();
      showToast(
        data.is_duplicate ? 'Duplicate Detected' : 'Upload Successful',
        data.message,
        data.is_duplicate ? 'warning' : 'success'
      );
    } else {
      showToast('Upload Failed', res.data.error || 'Server error occurred during upload.', 'danger');
    }
  } catch (err) {
    console.error("Upload error:", err);
    showToast('Upload Error', err.message || 'Network error occurred.', 'danger');
  } finally {
    uploadBtn.disabled = false;
    cancelBtn.disabled = false;
    spinner.classList.add('d-none');
    btnText.textContent = 'Upload to Cloud';
    setTimeout(() => {
      progressBar.classList.add('d-none');
      progressBarInner.style.width = '0%';
    }, 600);
  }
}

function displayDeduplicationResult(data) {
  const card = document.getElementById('dedupResultCard');
  const iconWrapper = document.getElementById('resultStatusIconWrapper');
  const icon = document.getElementById('resultStatusIcon');
  const title = document.getElementById('resultTitle');
  const badge = document.getElementById('resultBadge');
  const message = document.getElementById('resultMessage');

  document.getElementById('resultFilename').textContent = data.display_name;
  document.getElementById('resultSize').textContent = data.formatted_size;
  document.getElementById('resultHash').textContent = data.sha256_hash;
  document.getElementById('resultHash').title = data.sha256_hash;
  document.getElementById('resultSaved').textContent = data.is_duplicate ? `${data.formatted_saved} saved!` : '0 B (New Content)';

  if (data.is_duplicate) {
    // Duplicate detected styling
    card.className = 'card border-warning shadow rounded-4 p-4 mb-4 bg-white';
    iconWrapper.className = 'rounded-circle p-3 d-flex align-items-center justify-content-center bg-warning-subtle text-warning';
    icon.className = 'bi bi-intersect fs-2';
    title.textContent = 'Duplicate Content Detected!';
    badge.className = 'badge bg-warning text-dark py-2 px-3 rounded-pill';
    badge.textContent = 'Physical Upload Skipped';
    message.textContent = `Content SHA-256 fingerprint matched an existing cloud object. Reference linked without creating duplicate physical files in Firebase Storage.`;
  } else {
    // New physical upload styling
    card.className = 'card border-success shadow rounded-4 p-4 mb-4 bg-white';
    iconWrapper.className = 'rounded-circle p-3 d-flex align-items-center justify-content-center bg-success-subtle text-success';
    icon.className = 'bi bi-cloud-check-fill fs-2';
    title.textContent = 'New File Uploaded to Cloud!';
    badge.className = 'badge bg-success text-white py-2 px-3 rounded-pill';
    badge.textContent = 'Stored in Cloud';
    message.textContent = `New unique content fingerprint registered. File bytes uploaded directly to Firebase Cloud Storage at ${data.storage_path}.`;
  }

  card.classList.remove('d-none');
  card.scrollIntoView({ behavior: 'smooth' });
}

function formatBytesJs(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getIconForExt(ext) {
  const icons = {
    pdf: 'bi-file-earmark-pdf text-danger',
    doc: 'bi-file-earmark-word text-primary',
    docx: 'bi-file-earmark-word text-primary',
    txt: 'bi-file-earmark-text text-secondary',
    csv: 'bi-file-earmark-spreadsheet text-success',
    xls: 'bi-file-earmark-excel text-success',
    xlsx: 'bi-file-earmark-excel text-success',
    jpg: 'bi-file-earmark-image text-warning',
    jpeg: 'bi-file-earmark-image text-warning',
    png: 'bi-file-earmark-image text-info',
    zip: 'bi-file-earmark-zip text-dark',
  };
  return icons[ext] || 'bi-file-earmark text-muted';
}
