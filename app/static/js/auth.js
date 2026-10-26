/**
 * Authentication Form Handlers (Login, Register, Reset, Demo)
 */

function showAlert(message, type = 'danger') {
  const alertEl = document.getElementById('authAlert');
  if (!alertEl) return;
  alertEl.className = `alert alert-${type} py-2 small`;
  alertEl.textContent = message;
  alertEl.classList.remove('d-none');
}

function hideAlert() {
  const alertEl = document.getElementById('authAlert');
  if (alertEl) alertEl.classList.add('d-none');
}

function setLoading(btnId, isLoading, text = 'Submit') {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  const textEl = document.getElementById(`${btnId}Text`);
  const spinnerEl = document.getElementById(`${btnId}Spinner`);

  btn.disabled = isLoading;
  if (textEl) textEl.textContent = isLoading ? 'Please wait...' : text;
  if (spinnerEl) {
    if (isLoading) spinnerEl.classList.remove('d-none');
    else spinnerEl.classList.add('d-none');
  }
}

// -------------------------------------------------------------
// Quick Demo Login (for College Viva & Offline Evaluation)
// -------------------------------------------------------------
async function quickDemoLogin(userId, userName) {
  hideAlert();
  const email = `${userId}@clouddedup.com`;
  const demoToken = `demo-token-${userId}:${email}:${userName}`;

  localStorage.setItem('firebase_id_token', demoToken);
  setCookie('firebase_id_token', demoToken);

  const res = await apiRequest('/api/auth/sync-user', {
    method: 'POST',
    body: JSON.stringify({ name: userName }),
  });

  if (res.ok) {
    showToast('Signed In', `Logged in as ${userName} (${userId})`, 'success');
    setTimeout(() => {
      window.location.href = '/dashboard';
    }, 400);
  } else {
    showAlert(res.data.error || 'Failed to authenticate demo user.');
  }
}

// -------------------------------------------------------------
// Form Submissions
// -------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  // Login Form
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const email = document.getElementById('loginEmail').value.trim();
      const password = document.getElementById('loginPassword').value;

      if (!email || !password) {
        showAlert('Please fill in both email and password.');
        return;
      }

      setLoading('loginBtn', true, 'Sign In');

      try {
        if (isFirebaseConfigured) {
          // Live Firebase Authentication
          const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);
          const token = await userCredential.user.getIdToken();

          localStorage.setItem('firebase_id_token', token);
          setCookie('firebase_id_token', token);

          const syncRes = await apiRequest('/api/auth/sync-user', {
            method: 'POST',
            body: JSON.stringify({ name: userCredential.user.displayName || email.split('@')[0] }),
          });

          if (syncRes.ok && syncRes.data.success) {
            window.location.href = '/dashboard';
          } else {
            showAlert(syncRes.data.error || 'Database connection error. Please ensure MySQL is running.');
          }
        } else {
          // Offline / Demo mode fallback when live Firebase is not configured
          const uid = email.replace(/[^a-zA-Z0-9]/g, '_');
          await quickDemoLogin(uid, email.split('@')[0]);
        }
      } catch (err) {
        console.error("Login failed:", err);
        showAlert(err.message || 'Invalid email or password.');
      } finally {
        setLoading('loginBtn', false, 'Sign In');
      }
    });
  }

  // Register Form
  const registerForm = document.getElementById('registerForm');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const name = document.getElementById('registerName').value.trim();
      const email = document.getElementById('registerEmail').value.trim();
      const password = document.getElementById('registerPassword').value;
      const confirmPassword = document.getElementById('registerConfirmPassword').value;

      if (password !== confirmPassword) {
        showAlert('Passwords do not match.');
        return;
      }

      if (password.length < 6) {
        showAlert('Password must be at least 6 characters.');
        return;
      }

      setLoading('registerBtn', true, 'Register Account');

      try {
        if (isFirebaseConfigured) {
          const userCredential = await firebase.auth().createUserWithEmailAndPassword(email, password);
          await userCredential.user.updateProfile({ displayName: name });
          const token = await userCredential.user.getIdToken();

          localStorage.setItem('firebase_id_token', token);
          setCookie('firebase_id_token', token);

          const syncRes = await apiRequest('/api/auth/sync-user', {
            method: 'POST',
            body: JSON.stringify({ name }),
          });

          if (syncRes.ok && syncRes.data.success) {
            window.location.href = '/dashboard';
          } else {
            showAlert(syncRes.data.error || 'Database connection error. Please ensure MySQL is running.');
          }
        } else {
          // Offline / Demo mode registration
          const uid = email.replace(/[^a-zA-Z0-9]/g, '_');
          await quickDemoLogin(uid, name);
        }
      } catch (err) {
        console.error("Registration failed:", err);
        showAlert(err.message || 'Registration failed. Please try again.');
      } finally {
        setLoading('registerBtn', false, 'Register Account');
      }
    });
  }

  // Forgot Password Form
  const forgotForm = document.getElementById('forgotPasswordForm');
  if (forgotForm) {
    forgotForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const email = document.getElementById('resetEmail').value.trim();
      if (!email) {
        showAlert('Please provide your email address.');
        return;
      }

      setLoading('resetBtn', true, 'Send Reset Link');

      try {
        if (isFirebaseConfigured) {
          await firebase.auth().sendPasswordResetEmail(email);
          showAlert('Password reset link sent to your email!', 'success');
        } else {
          showAlert('Demo Mode: Password reset link simulated successfully.', 'success');
        }
      } catch (err) {
        console.error("Password reset error:", err);
        showAlert(err.message || 'Could not send reset email.');
      } finally {
        setLoading('resetBtn', false, 'Send Reset Link');
      }
    });
  }
});
