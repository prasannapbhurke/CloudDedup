import os
import mimetypes
from werkzeug.utils import secure_filename
from flask import current_app


def validate_file_upload(file_storage):
    """
    Validates uploaded file against size, extension, and content rules.

    Args:
        file_storage (werkzeug.datastructures.FileStorage): The incoming uploaded file.

    Returns:
        tuple: (is_valid: bool, error_message: str or None, sanitized_filename: str)
    """
    if not file_storage or not file_storage.filename:
        return False, "No file was selected for upload.", ""

    raw_filename = file_storage.filename.strip()
    sanitized_name = secure_filename(raw_filename)

    if not sanitized_name:
        sanitized_name = "uploaded_file"

    # Check extension
    if "." not in sanitized_name:
        return False, "Files without an extension are not allowed.", sanitized_name

    ext = sanitized_name.rsplit(".", 1)[1].lower()
    allowed_extensions = current_app.config.get("ALLOWED_EXTENSIONS", set())

    if ext not in allowed_extensions:
        allowed_str = ", ".join(sorted(allowed_extensions))
        return (
            False,
            f"File extension '.{ext}' is not permitted. Allowed types: {allowed_str}.",
            sanitized_name,
        )

    # Check file size (seek to end and back to 0)
    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)

    if file_size == 0:
        return False, "Empty files (0 bytes) cannot be uploaded.", sanitized_name

    max_size = current_app.config.get("MAX_CONTENT_LENGTH", 50 * 1024 * 1024)
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        return (
            False,
            f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed limit of {max_mb:.0f} MB.",
            sanitized_name,
        )

    # Determine / sanitize MIME type
    guessed_type, _ = mimetypes.guess_type(sanitized_name)
    mime_type = file_storage.content_type or guessed_type or "application/octet-stream"

    return True, None, sanitized_name
