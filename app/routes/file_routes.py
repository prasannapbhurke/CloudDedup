import logging
from flask import Blueprint, render_template, request, jsonify, g, send_file
from app.middleware.authentication import require_auth
from app.services.file_management_service import FileManagementService

logger = logging.getLogger(__name__)

file_bp = Blueprint("files", __name__)


@file_bp.route("/my-files")
def my_files_page():
    """Renders the My Files management page."""
    return render_template("my_files.html")


@file_bp.route("/api/files", methods=["GET"])
@require_auth
def list_files_api():
    """
    Retrieves files for the logged-in user with search, filter, sort, and pagination.
    """
    search = request.args.get("search", "").strip()
    file_type = request.args.get("type", "").strip()
    status = request.args.get("status", "").strip()
    sort_by = request.args.get("sort", "date").strip()
    sort_order = request.args.get("order", "desc").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    result = FileManagementService.get_user_files(
        user_id=g.current_user.id,
        search=search,
        file_type=file_type,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page,
    )
    return jsonify({"success": True, **result})


@file_bp.route("/api/files/<int:file_id>/download", methods=["GET"])
@require_auth
def download_file_api(file_id):
    """
    Downloads the underlying cloud object using the user's specific display filename.
    Strictly verifies ownership to prevent accessing other users' references.
    """
    try:
        stream, display_name, mime_type = FileManagementService.download_file_reference(
            user_id=g.current_user.id,
            reference_id=file_id,
        )
        return send_file(
            stream,
            as_attachment=True,
            download_name=display_name,
            mimetype=mime_type or "application/octet-stream",
        )
    except PermissionError as e:
        return jsonify({"success": False, "error": str(e)}), 403
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.error(f"Download failed for file ID {file_id}: {e}")
        return jsonify({"success": False, "error": f"Download failed: {str(e)}"}), 500


@file_bp.route("/api/files/<int:file_id>", methods=["DELETE"])
@require_auth
def delete_file_api(file_id):
    """
    Deletes the user's file reference.
    Safely purges the physical cloud object only if no other references exist anywhere.
    """
    try:
        result = FileManagementService.delete_file_reference(
            user_id=g.current_user.id,
            reference_id=file_id,
        )
        return jsonify(result), 200
    except PermissionError as e:
        return jsonify({"success": False, "error": str(e)}), 403
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.error(f"Deletion failed for file ID {file_id}: {e}")
        return jsonify({"success": False, "error": f"Deletion failed: {str(e)}"}), 500
