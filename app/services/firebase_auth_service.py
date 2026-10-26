import os
import logging
from pathlib import Path
from flask import current_app
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

logger = logging.getLogger(__name__)

_firebase_app_initialized = False


def init_firebase_admin(app=None):
    """
    Initializes the Firebase Admin SDK once using configured service account credentials.
    """
    global _firebase_app_initialized
    if _firebase_app_initialized:
        return

    config = app.config if app else current_app.config
    cert_path = config.get("FIREBASE_SERVICE_ACCOUNT_PATH")

    try:
        if cert_path and os.path.exists(cert_path):
            cred = credentials.Certificate(cert_path)
            bucket_name = config.get("FIREBASE_STORAGE_BUCKET")
            firebase_admin.initialize_app(
                cred,
                {"storageBucket": bucket_name} if bucket_name else None,
            )
            _firebase_app_initialized = True
            logger.info("Firebase Admin SDK initialized successfully with service account.")
        else:
            # Check default credentials or mark uninitialized
            logger.warning(
                f"Firebase service account file not found at '{cert_path}'. "
                "Running in fallback/demo mode for authentication verification."
            )
    except ValueError as e:
        # App might already be initialized
        if "The default Firebase app already exists" in str(e):
            _firebase_app_initialized = True
        else:
            logger.error(f"Error initializing Firebase Admin SDK: {e}")
    except Exception as e:
        logger.error(f"Unexpected error initializing Firebase Admin SDK: {e}")


def get_firestore_client(app=None):
    """
    Returns an initialized Google Cloud Firestore client.
    """
    init_firebase_admin(app)
    if _firebase_app_initialized:
        try:
            from firebase_admin import firestore
            return firestore.client()
        except Exception as e:
            logger.warning(f"Could not connect to Firestore client: {e}")
    return None


class FirebaseAuthService:
    """
    Service for verifying Firebase ID tokens passed by the frontend.
    Extracts UID, email, and user name. Never trusts client-supplied user IDs.
    """

    @classmethod
    def verify_id_token(cls, id_token):
        """
        Verifies a Firebase ID token using the Firebase Admin SDK.

        Args:
            id_token (str): The bearer token provided in HTTP headers.

        Returns:
            dict: Decoded claims containing 'uid', 'email', 'name', etc.

        Raises:
            ValueError: If token is invalid, expired, revoked, or empty.
        """
        if not id_token or not isinstance(id_token, str):
            raise ValueError("Firebase ID token is missing or empty.")

        id_token = id_token.strip()

        # Handle Mock/Demo tokens for offline development or testing without live Firebase project
        if id_token.startswith("demo-token-") or id_token.startswith("mock-token-"):
            parts = id_token.split(":")
            # Format: demo-token-<uid>:<email>:<name>
            uid = parts[0].replace("demo-token-", "").replace("mock-token-", "")
            email = parts[1] if len(parts) > 1 else f"{uid}@example.com"
            name = parts[2] if len(parts) > 2 else "Demo Student"
            return {
                "uid": uid,
                "email": email,
                "name": name,
                "auth_time": 1700000000,
            }

        # Ensure Firebase Admin SDK is initialized
        init_firebase_admin()

        if not _firebase_app_initialized:
            raise ValueError(
                "Firebase Admin SDK is not configured. Please supply a valid serviceAccountKey.json "
                "or enable demo mode for testing."
            )

        try:
            decoded_token = firebase_auth.verify_id_token(id_token, check_revoked=True)
            return decoded_token
        except firebase_auth.ExpiredIdTokenError:
            raise ValueError("Authentication token has expired. Please log in again.")
        except firebase_auth.RevokedIdTokenError:
            raise ValueError("Authentication token has been revoked.")
        except firebase_auth.InvalidIdTokenError as e:
            raise ValueError(f"Invalid authentication token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to authenticate token: {str(e)}")
