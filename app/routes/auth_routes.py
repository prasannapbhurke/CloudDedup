from flask import Blueprint, render_template, request, jsonify, g
from app.extensions import db
from app.middleware.authentication import require_auth, get_token_from_request, get_or_create_user
from app.services.firebase_auth_service import FirebaseAuthService

auth_bp = Blueprint("auth", __name__)


# -------------------------------------------------------------
# Frontend HTML Page Routes
# -------------------------------------------------------------
@auth_bp.route("/login")
def login_page():
    return render_template("login.html")


@auth_bp.route("/register")
def register_page():
    return render_template("register.html")


@auth_bp.route("/forgot-password")
def forgot_password_page():
    return render_template("forgot_password.html")


# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------
@auth_bp.route("/api/auth/sync-user", methods=["POST"])
def sync_user():
    """
    Called immediately by the frontend after a successful Firebase Auth login or register.
    Derives user identity solely from the verified Firebase ID Token.
    Synchronizes the user record in MySQL.
    """
    token = get_token_from_request()
    if not token:
        return jsonify({"success": False, "error": "Missing authorization token."}), 401

    try:
        decoded_token = FirebaseAuthService.verify_id_token(token)
        user = get_or_create_user(decoded_token)

        # Allow updating name if provided from registration
        data = request.get_json(silent=True) or {}
        custom_name = data.get("name")
        if custom_name and custom_name.strip() and user.name != custom_name.strip():
            user.name = custom_name.strip()
            db.session.commit()

        return jsonify({
            "success": True,
            "message": "User synchronized successfully.",
            "user": user.to_dict(),
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 401
    except Exception as e:
        return jsonify({"success": False, "error": f"Synchronization error: {str(e)}"}), 500


@auth_bp.route("/api/auth/me", methods=["GET"])
@require_auth
def get_current_user():
    """
    Returns the currently authenticated user's profile from MySQL.
    """
    return jsonify({
        "success": True,
        "user": g.current_user.to_dict(),
    })
