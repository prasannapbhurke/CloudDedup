import logging
from flask import Blueprint, render_template, request, jsonify, g
from app.middleware.authentication import require_auth
from app.utils.validators import validate_file_upload
from app.services.deduplication_service import DeduplicationService

logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload")
def upload_page():
    """Renders the dedicated File Upload interface."""
    return render_template("upload.html")


@upload_bp.route("/api/files/upload", methods=["POST"])
@require_auth
def upload_file_api():
    """
    Handles file upload, validation, cryptographic hashing, and deduplication.
    All deduplication decisions are executed on the backend.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in the upload request."}), 400

    uploaded_file = request.files["file"]

    # Validate file size, extension, and content
    is_valid, error_msg, sanitized_filename = validate_file_upload(uploaded_file)
    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    try:
        # Process through Deduplication Engine
        result = DeduplicationService.process_file_upload(
            user=g.current_user,
            file_storage=uploaded_file,
            display_name=sanitized_filename,
        )
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error during upload processing: {e}")
        return jsonify({"success": False, "error": f"Upload failed: {str(e)}"}), 500
