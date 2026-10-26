/**
 * Firebase Client SDK Configuration
 *
 * Replace the values below with your Firebase Web App configuration from:
 * Firebase Console > Project Settings > General > Your Apps > Web App
 */
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAtQ5akf3_FJ41Vc_w3x_ykP28ulj1P9cY",
  authDomain: "clouddedup-project.firebaseapp.com",
  projectId: "clouddedup-project",
  storageBucket: "clouddedup-project.firebasestorage.app",
  messagingSenderId: "115843939902",
  appId: "1:115843939902:web:01733ce819169b069e5b6f",
  measurementId: "G-P4P898Q92D"
};
// Check if Firebase is available and initialize
let isFirebaseConfigured = false;

try {
  if (typeof firebase !== 'undefined' && firebase.initializeApp) {
    // Check if real API key is configured or default placeholder
    if (firebaseConfig.apiKey && !firebaseConfig.apiKey.includes("DemoKeyReplace")) {
      firebase.initializeApp(firebaseConfig);
      isFirebaseConfigured = true;
      console.log("[Firebase] Client SDK initialized with live configuration.");
    } else {
      console.warn(
        "[Firebase] Placeholder configuration detected. " +
        "Running in demonstration/offline mode for testing and grading."
      );
    }
  }
} catch (e) {
  console.error("[Firebase] Initialization error:", e);
}
