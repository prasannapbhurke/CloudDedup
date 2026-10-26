import logging
from functools import wraps
from flask import request, jsonify, g, redirect, url_for
from app.extensions import db
from app.models.user import User
from app.services.firebase_auth_service import FirebaseAuthService

logger = logging.getLogger(__name__)


def get_token_from_request():
    """
    Extracts the Firebase ID token from the Authorization header or session cookie.
    Header format: Authorization: Bearer <token>
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split("Bearer ")[1].strip()

    # Also check cookie (helpful for direct file download links and SSR navigation)
    cookie_token = request.cookies.get("firebase_id_token")
    if cookie_token:
        return cookie_token.strip()

    return None


def get_or_create_user(decoded_token):
    """
    Retrieves or creates a MySQL user record based on the verified Firebase UID.
    Never stores passwords in MySQL.
    """
    uid = decoded_token.get("uid")
    if not uid:
        return None

    email = decoded_token.get("email", f"{uid}@example.com")
    name = decoded_token.get("name") or email.split("@")[0].title()

    user = User.query.filter_by(firebase_uid=uid).first()

    if not user:
        # Check by email in case of re-linking
        user = User.query.filter_by(email=email).first()
        if user:
            user.firebase_uid = uid
        else:
            user = User(
                firebase_uid=uid,
                name=name,
                email=email,
            )
            db.session.add(user)

        try:
            db.session.commit()
            logger.info(f"Synchronized new user in MySQL: {email} (UID: {uid})")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to auto-create user in MySQL: {e}")
            user = User.query.filter_by(firebase_uid=uid).first()

    return user


def require_auth(f):
    """
    Decorator for protected REST API endpoints.
    Verifies Firebase ID token, resolves MySQL user, and attaches it to g.current_user.
    Returns JSON error responses on failure.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return (
                jsonify({
                    "success": False,
                    "error": "Authentication required. Missing Bearer token.",
                }),
                401,
            )

        try:
            decoded_token = FirebaseAuthService.verify_id_token(token)
            user = get_or_create_user(decoded_token)

            if not user:
                return (
                    jsonify({
                        "success": False,
                        "error": "User synchronization failed.",
                    }),
                    401,
                )

            # Store in Flask request context
            g.firebase_user = decoded_token
            g.current_user = user

        except ValueError as e:
            return (
                jsonify({
                    "success": False,
                    "error": str(e),
                }),
                401,
            )
        except Exception as e:
            logger.error(f"Unexpected auth error: {e}")
            return (
                jsonify({
                    "success": False,
                    "error": "Authentication verification failed.",
                }),
                401,
            )

        return f(*args, **kwargs)

    return decorated_function
