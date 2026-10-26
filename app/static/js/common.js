/**
 * CloudDedup Common Client Utilities
 * Handles Authentication state, API headers, Toast notifications, and Modals.
 */

// Helper to set Cookie
function setCookie(name, value, days = 7) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/; SameSite=Lax';
}

function getCookie(name) {
  return document.cookie.split('; ').reduce((r, v) => {
    const parts = v.split('=');
    return parts[0] === name ? decodeURIComponent(parts[1]) : r;
  }, '');
}

function deleteCookie(name) {
  document.cookie = name + '=; Max-Age=-99999999; path=/;';
}

// Get active ID token from LocalStorage, Cookie, or Firebase
async function getAuthToken() {
  if (isFirebaseConfigured && firebase.auth().currentUser) {
    try {
      const token = await firebase.auth().currentUser.getIdToken();
      localStorage.setItem('firebase_id_token', token);
      setCookie('firebase_id_token', token);
      return token;
    } catch (e) {
      console.error("Error refreshing token:", e);
    }
  }

  return localStorage.getItem('firebase_id_token') || getCookie('firebase_id_token') || null;
}

// Wrapper for all authenticated backend API calls
async function apiRequest(endpoint, options = {}) {
  const token = await getAuthToken();

  const headers = options.headers || {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // If body is FormData, do not set Content-Type header (browser sets boundary automatically)
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  options.headers = headers;

  try {
    const response = await fetch(endpoint, options);
    const data = await response.json().catch(() => ({ success: false, error: "Failed to parse JSON response." }));

    if (response.status === 401) {
      console.warn("Session expired or unauthorized for endpoint:", endpoint);
      localStorage.removeItem('firebase_id_token');
      deleteCookie('firebase_id_token');
      // Do not redirect if we are already on login/register or if the request was an auth sync check
      if (
        !window.location.pathname.includes('/login') &&
        !window.location.pathname.includes('/register') &&
        !endpoint.includes('/api/auth/')
      ) {
        window.location.href = '/login';
      }
    }

    return { ok: response.ok, status: response.status, data };
  } catch (err) {
    console.error(`API Request Error [${endpoint}]:`, err);
    return { ok: false, status: 0, data: { success: false, error: err.message || "Network error occurred." } };
  }
}

// Toast Notification Manager
function showToast(title, message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const bgClasses = {
    success: 'text-bg-success',
    danger: 'text-bg-danger',
    warning: 'text-bg-warning text-dark',
    info: 'text-bg-primary',
  };

  const bgClass = bgClasses[type] || 'text-bg-dark';

  const toastId = 'toast_' + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg mb-2" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <div class="fw-bold mb-1">${title}</div>
          <div class="small">${message}</div>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  container.insertAdjacentHTML('beforeend', toastHtml);
  const toastEl = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
  toast.show();

  toastEl.addEventListener('hidden.bs.toast', () => {
    toastEl.remove();
  });
}

// Reusable Confirmation Modal
let currentConfirmCallback = null;
function showConfirmModal(title, message, onConfirm) {
  const modalEl = document.getElementById('confirmModal');
  if (!modalEl) {
    if (confirm(message)) onConfirm();
    return;
  }

  document.getElementById('confirmModalTitle').textContent = title;
  document.getElementById('confirmModalMessage').textContent = message;
  currentConfirmCallback = onConfirm;

  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

document.addEventListener('DOMContentLoaded', () => {
  const confirmBtn = document.getElementById('confirmModalBtn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', () => {
      const modalEl = document.getElementById('confirmModal');
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
      if (typeof currentConfirmCallback === 'function') {
        currentConfirmCallback();
        currentConfirmCallback = null;
      }
    });
  }

  // Mobile sidebar toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const appSidebar = document.getElementById('appSidebar');
  const sidebarBackdrop = document.getElementById('sidebarBackdrop');

  if (sidebarToggle && appSidebar && sidebarBackdrop) {
    sidebarToggle.addEventListener('click', () => {
      appSidebar.classList.toggle('show');
      sidebarBackdrop.classList.toggle('show');
    });

    sidebarBackdrop.addEventListener('click', () => {
      appSidebar.classList.remove('show');
      sidebarBackdrop.classList.remove('show');
    });
  }

  // Initialize Auth Check for Protected Pages
  initAuthGuard();
});

// User Session and Auth State Observer
async function initAuthGuard() {
  const currentPath = window.location.pathname;
  const publicPaths = ['/login', '/register', '/forgot-password'];
  const isPublicPage = publicPaths.some(p => currentPath === p);

  // If Firebase is configured, observe state
  if (isFirebaseConfigured) {
    firebase.auth().onAuthStateChanged(async (user) => {
      if (user) {
        try {
          const token = await user.getIdToken();
          localStorage.setItem('firebase_id_token', token);
          setCookie('firebase_id_token', token);

          // Sync with MySQL
          const syncRes = await apiRequest('/api/auth/sync-user', {
            method: 'POST',
            body: JSON.stringify({ name: user.displayName || user.email.split('@')[0] }),
          });

          if (syncRes.ok && syncRes.data.success) {
            updateUserProfileUI({
              name: syncRes.data.user.name || user.displayName || user.email.split('@')[0],
              email: syncRes.data.user.email || user.email,
            });

            if (isPublicPage) {
              window.location.href = '/dashboard';
            }
          } else {
            console.warn("Backend user sync unsuccessful:", syncRes.data.error);
            // If backend rejected sync, sign out to avoid redirect bounce loop
            localStorage.removeItem('firebase_id_token');
            deleteCookie('firebase_id_token');
            if (!isPublicPage) {
              window.location.href = '/login';
            }
          }
        } catch (err) {
          console.error("Auth state processing error:", err);
        }
      } else {
        localStorage.removeItem('firebase_id_token');
        deleteCookie('firebase_id_token');
        if (!isPublicPage) {
          window.location.href = '/login';
        }
      }
    });
  } else {
    // Demo / Offline mode check
    const demoToken = localStorage.getItem('firebase_id_token') || getCookie('firebase_id_token');
    if (!demoToken && !isPublicPage) {
      window.location.href = '/login';
    } else if (demoToken) {
      // Fetch user profile from backend
      const res = await apiRequest('/api/auth/me');
      if (res.ok && res.data.user) {
        updateUserProfileUI(res.data.user);
        if (isPublicPage) {
          window.location.href = '/dashboard';
        }
      } else if (!isPublicPage) {
        window.location.href = '/login';
      }
    }
  }
}

// Update Topbar and Sidebar Profile Elements
function updateUserProfileUI(user) {
  const nameEl = document.getElementById('sidebarUserName');
  const emailEl = document.getElementById('sidebarUserEmail');
  const avatarEl = document.getElementById('sidebarUserAvatar');

  if (nameEl) nameEl.textContent = user.name || 'User';
  if (emailEl) emailEl.textContent = user.email || '';
  if (avatarEl) {
    const initial = (user.name || user.email || 'U').charAt(0).toUpperCase();
    avatarEl.textContent = initial;
  }
}

// Global Logout Handler
async function logoutUser() {
  showConfirmModal('Log Out', 'Are you sure you want to sign out of CloudDedup?', async () => {
    try {
      if (isFirebaseConfigured) {
        await firebase.auth().signOut();
      }
    } catch (e) {
      console.warn("Firebase signout error:", e);
    }

    localStorage.removeItem('firebase_id_token');
    deleteCookie('firebase_id_token');
    window.location.href = '/login';
  });
}
