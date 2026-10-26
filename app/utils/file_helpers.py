def format_bytes(size_in_bytes):
    """
    Formats a byte integer into human-readable size string (B, KB, MB, GB, TB).
    Example: 10485760 -> '10.00 MB'
    """
    if size_in_bytes is None or size_in_bytes < 0:
        return "0 B"

    size = float(size_in_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0 or unit == "TB":
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.2f} {unit}"
        size /= 1024.0

    return f"{size_in_bytes} B"


def shorten_hash(sha256_hex, length=12):
    """
    Returns a shortened representation of the SHA-256 hash for UI display.
    Example: 'a8f23c9d1204...'
    """
    if not sha256_hex:
        return ""
    if len(sha256_hex) <= length:
        return sha256_hex
    return f"{sha256_hex[:length]}..."


def get_file_type_category(filename):
    """
    Returns a generalized category for a file based on its extension.
    Useful for Chart.js distributions and UI badges.
    """
    if not filename or "." not in filename:
        return "Other"

    ext = filename.rsplit(".", 1)[1].lower()

    categories = {
        "pdf": "Document (PDF)",
        "doc": "Document (Word)",
        "docx": "Document (Word)",
        "txt": "Text",
        "csv": "Spreadsheet (CSV)",
        "xls": "Spreadsheet (Excel)",
        "xlsx": "Spreadsheet (Excel)",
        "jpg": "Image (JPEG)",
        "jpeg": "Image (JPEG)",
        "png": "Image (PNG)",
        "zip": "Archive (ZIP)",
    }
    return categories.get(ext, "Other")


def get_file_icon_class(filename):
    """
    Returns a Bootstrap icon class corresponding to the file extension.
    """
    if not filename or "." not in filename:
        return "bi-file-earmark"

    ext = filename.rsplit(".", 1)[1].lower()

    icons = {
        "pdf": "bi-file-earmark-pdf text-danger",
        "doc": "bi-file-earmark-word text-primary",
        "docx": "bi-file-earmark-word text-primary",
        "txt": "bi-file-earmark-text text-secondary",
        "csv": "bi-file-earmark-spreadsheet text-success",
        "xls": "bi-file-earmark-excel text-success",
        "xlsx": "bi-file-earmark-excel text-success",
        "jpg": "bi-file-earmark-image text-warning",
        "jpeg": "bi-file-earmark-image text-warning",
        "png": "bi-file-earmark-image text-info",
        "zip": "bi-file-earmark-zip text-dark",
    }
    return icons.get(ext, "bi-file-earmark text-muted")
