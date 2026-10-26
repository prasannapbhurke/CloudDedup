import logging
from sqlalchemy import or_
from app.extensions import db
from app.models.stored_file import StoredFile
from app.models.file_reference import FileReference
from app.services.firebase_storage_service import FirebaseStorageService
from app.utils.file_helpers import format_bytes, shorten_hash, get_file_type_category, get_file_icon_class

logger = logging.getLogger(__name__)


class FileManagementService:
    """
    Service for querying, downloading, and safely deleting user file references.
    Enforces strict user isolation — users can only view, download, or delete their own references.
    """

    @classmethod
    def get_user_files(
        cls,
        user_id,
        search="",
        file_type="",
        status="",
        sort_by="date",
        sort_order="desc",
        page=1,
        per_page=50,
    ):
        """
        Retrieves user's file references with search, filtering, and sorting.

        Args:
            user_id (int): Primary key of the authenticated user in MySQL.
            search (str): Filter by display filename substring.
            file_type (str): Extension filter (e.g. 'pdf', 'png').
            status (str): 'original', 'duplicate', or 'all'.
            sort_by (str): 'name', 'size', or 'date'.
            sort_order (str): 'asc' or 'desc'.

        Returns:
            dict: List of file dictionaries with metadata and pagination info.
        """
        query = (
            db.session.query(FileReference, StoredFile)
            .join(StoredFile, FileReference.stored_file_id == StoredFile.id)
            .filter(FileReference.user_id == user_id)
        )

        # Search filter
        if search:
            query = query.filter(FileReference.display_name.ilike(f"%{search.strip()}%"))

        # File type filter
        if file_type and file_type != "all":
            query = query.filter(FileReference.display_name.ilike(f"%.{file_type.strip()}"))

        # Status filter (original vs duplicate)
        if status == "original":
            query = query.filter(FileReference.is_duplicate.is_(False))
        elif status == "duplicate":
            query = query.filter(FileReference.is_duplicate.is_(True))

        # Sorting
        if sort_by == "name":
            order_col = FileReference.display_name.asc() if sort_order == "asc" else FileReference.display_name.desc()
        elif sort_by == "size":
            order_col = StoredFile.file_size.asc() if sort_order == "asc" else StoredFile.file_size.desc()
        else:  # default 'date'
            order_col = FileReference.uploaded_at.asc() if sort_order == "asc" else FileReference.uploaded_at.desc()

        query = query.order_by(order_col)

        # Pagination
        total_items = query.count()
        paginated_records = query.offset((page - 1) * per_page).limit(per_page).all()

        files_list = []
        for ref, stored in paginated_records:
            files_list.append({
                "id": ref.id,
                "display_name": ref.display_name,
                "file_size": stored.file_size,
                "formatted_size": format_bytes(stored.file_size),
                "sha256_hash": stored.sha256_hash,
                "short_hash": shorten_hash(stored.sha256_hash),
                "is_duplicate": ref.is_duplicate,
                "status_label": "Duplicate" if ref.is_duplicate else "Original",
                "uploaded_at": ref.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if ref.uploaded_at else "",
                "category": get_file_type_category(ref.display_name),
                "icon_class": get_file_icon_class(ref.display_name),
                "stored_file_id": stored.id,
            })

        return {
            "files": files_list,
            "total_items": total_items,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_items + per_page - 1) // per_page if total_items > 0 else 1,
        }

    @classmethod
    def get_reference_for_user(cls, user_id, reference_id):
        """
        Retrieves a single FileReference ensuring it belongs to the given user.
        Prevents unauthorized access to other users' file references.
        """
        ref = (
            FileReference.query.filter_by(id=reference_id, user_id=user_id)
            .first()
        )
        return ref

    @classmethod
    def download_file_reference(cls, user_id, reference_id):
        """
        Fetches the byte stream and original display name for downloading.
        Validates user ownership before accessing cloud storage.

        Returns:
            tuple: (file_stream: io.BytesIO, filename: str, mime_type: str)

        Raises:
            PermissionError: If reference does not belong to the user.
            FileNotFoundError: If reference or cloud object is missing.
        """
        ref = cls.get_reference_for_user(user_id, reference_id)
        if not ref:
            raise PermissionError("Access denied: You do not own this file reference or it does not exist.")

        stored = ref.stored_file
        if not stored:
            raise FileNotFoundError("Underlying storage metadata is missing.")

        stream = FirebaseStorageService.download_file(stored.storage_path)
        return stream, ref.display_name, stored.mime_type

    @classmethod
    def delete_file_reference(cls, user_id, reference_id):
        """
        Deletes a user's file reference safely.
        If no other references exist anywhere in the application, deletes the physical
        object from Firebase Cloud Storage and deletes the StoredFile row.

        Returns:
            dict: Summary of deletion (whether physical file was purged or retained).

        Raises:
            PermissionError: If reference does not belong to user.
            FileNotFoundError: If reference not found.
        """
        ref = cls.get_reference_for_user(user_id, reference_id)
        if not ref:
            raise PermissionError("Access denied: You do not own this file reference or it does not exist.")

        stored = ref.stored_file
        stored_file_id = stored.id
        storage_path = stored.storage_path
        filename = ref.display_name

        try:
            # Delete the user's logical reference
            db.session.delete(ref)
            db.session.flush()

            # Check remaining references across the ENTIRE system
            remaining_refs = FileReference.query.filter_by(stored_file_id=stored_file_id).count()

            physical_purged = False
            if remaining_refs == 0:
                # Last reference deleted! Clean up physical cloud object and stored_files record
                logger.info(
                    f"No references remain for content {stored.sha256_hash[:12]}. Purging from cloud storage..."
                )
                FirebaseStorageService.delete_file(storage_path)
                db.session.delete(stored)
                physical_purged = True
            else:
                # Update cached reference count
                stored.reference_count = remaining_refs
                logger.info(
                    f"Reference deleted. {remaining_refs} reference(s) still active for {stored.sha256_hash[:12]}."
                )

            db.session.commit()

            return {
                "success": True,
                "message": f"File '{filename}' successfully deleted.",
                "physical_purged": physical_purged,
                "remaining_system_references": remaining_refs,
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete file reference {reference_id}: {e}")
            raise e
