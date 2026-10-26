import logging
import mimetypes
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.stored_file import StoredFile
from app.models.file_reference import FileReference
from app.models.upload_event import UploadEvent
from app.services.hashing_service import HashingService
from app.services.firebase_storage_service import FirebaseStorageService
from app.utils.file_helpers import format_bytes, shorten_hash

logger = logging.getLogger(__name__)


class DeduplicationService:
    """
    Core Deduplication Engine.
    Coordinates SHA-256 fingerprinting, physical cloud object storage,
    MySQL metadata recording, and user-isolated file references.
    """

    @classmethod
    def process_file_upload(cls, user, file_storage, display_name):
        """
        Processes an incoming uploaded file through the deduplication pipeline.

        Args:
            user (User): The authenticated MySQL User instance.
            file_storage (FileStorage): The uploaded file stream from Flask request.
            display_name (str): Sanitized filename chosen by the user.

        Returns:
            dict: Comprehensive result including deduplication status, saved bytes,
                  storage path, and reference details.

        Raises:
            Exception: If validation, hashing, cloud upload, or database commit fails.
        """
        # Step 1: Calculate SHA-256 hash and file size in bytes
        sha256_hash, file_size = HashingService.calculate_sha256(file_storage.stream)
        guessed_type, _ = mimetypes.guess_type(display_name)
        mime_type = file_storage.content_type or guessed_type or "application/octet-stream"

        # Step 2: Check if this content hash already exists in MySQL stored_files
        existing_stored = StoredFile.query.filter_by(sha256_hash=sha256_hash).first()

        storage_path = f"objects/{sha256_hash}"

        # -----------------------------------------------------------------
        # CASE B: DUPLICATE CONTENT DETECTED
        # -----------------------------------------------------------------
        if existing_stored:
            logger.info(
                f"[DEDUPLICATION HIT] Content hash {sha256_hash[:12]} already exists. "
                f"Skipping physical cloud upload for '{display_name}'."
            )

            # Ensure cloud object actually exists (healing / sanity check)
            if not FirebaseStorageService.object_exists(existing_stored.storage_path):
                logger.warning(
                    f"Storage object {existing_stored.storage_path} missing in cloud. Re-uploading content..."
                )
                FirebaseStorageService.upload_file(file_storage.stream, existing_stored.storage_path, mime_type)

            try:
                # Increment reference counter on the physical object
                existing_stored.reference_count += 1

                # Create a new logical file reference for this user
                file_ref = FileReference(
                    user_id=user.id,
                    stored_file_id=existing_stored.id,
                    display_name=display_name,
                    is_duplicate=True,
                )
                db.session.add(file_ref)

                # Record upload audit history
                upload_event = UploadEvent(
                    user_id=user.id,
                    stored_file_id=existing_stored.id,
                    original_filename=display_name,
                    file_size=file_size,
                    sha256_hash=sha256_hash,
                    event_type="duplicate_detected",
                )
                db.session.add(upload_event)

                db.session.commit()

                return {
                    "success": True,
                    "is_duplicate": True,
                    "message": f"Duplicate content detected! Linked to existing cloud object. Physical upload skipped.",
                    "display_name": display_name,
                    "sha256_hash": sha256_hash,
                    "short_hash": shorten_hash(sha256_hash),
                    "file_size": file_size,
                    "formatted_size": format_bytes(file_size),
                    "storage_saved_bytes": file_size,
                    "formatted_saved": format_bytes(file_size),
                    "reference_id": file_ref.id,
                    "stored_file_id": existing_stored.id,
                    "storage_path": existing_stored.storage_path,
                }

            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to record duplicate reference in database: {e}")
                raise e

        # -----------------------------------------------------------------
        # CASE A: NEW UNIQUE CONTENT
        # -----------------------------------------------------------------
        logger.info(
            f"[NEW CONTENT] Content hash {sha256_hash[:12]} is unique. Uploading to Firebase Cloud Storage..."
        )

        physical_upload_done = False
        try:
            # 1. Upload unique physical file to Firebase Cloud Storage
            FirebaseStorageService.upload_file(file_storage.stream, storage_path, mime_type)
            physical_upload_done = True

            # 2. Create StoredFile record in MySQL
            new_stored = StoredFile(
                sha256_hash=sha256_hash,
                file_size=file_size,
                storage_path=storage_path,
                mime_type=mime_type,
                reference_count=1,
            )
            db.session.add(new_stored)
            db.session.flush()  # Flush to obtain new_stored.id

            # 3. Create FileReference for the user
            file_ref = FileReference(
                user_id=user.id,
                stored_file_id=new_stored.id,
                display_name=display_name,
                is_duplicate=False,
            )
            db.session.add(file_ref)

            # 4. Record upload event
            upload_event = UploadEvent(
                user_id=user.id,
                stored_file_id=new_stored.id,
                original_filename=display_name,
                file_size=file_size,
                sha256_hash=sha256_hash,
                event_type="new_upload",
            )
            db.session.add(upload_event)

            db.session.commit()

            return {
                "success": True,
                "is_duplicate": False,
                "message": "New unique file uploaded to Firebase Cloud Storage successfully.",
                "display_name": display_name,
                "sha256_hash": sha256_hash,
                "short_hash": shorten_hash(sha256_hash),
                "file_size": file_size,
                "formatted_size": format_bytes(file_size),
                "storage_saved_bytes": 0,
                "formatted_saved": "0 B",
                "reference_id": file_ref.id,
                "stored_file_id": new_stored.id,
                "storage_path": storage_path,
            }

        except IntegrityError:
            # Concurrency race condition: another thread uploaded the exact same file simultaneously
            db.session.rollback()
            logger.info("Concurrent upload race condition caught. Re-fetching existing stored file.")
            existing_stored = StoredFile.query.filter_by(sha256_hash=sha256_hash).first()
            if existing_stored:
                existing_stored.reference_count += 1
                file_ref = FileReference(
                    user_id=user.id,
                    stored_file_id=existing_stored.id,
                    display_name=display_name,
                    is_duplicate=True,
                )
                db.session.add(file_ref)
                upload_event = UploadEvent(
                    user_id=user.id,
                    stored_file_id=existing_stored.id,
                    original_filename=display_name,
                    file_size=file_size,
                    sha256_hash=sha256_hash,
                    event_type="duplicate_detected",
                )
                db.session.add(upload_event)
                db.session.commit()
                return {
                    "success": True,
                    "is_duplicate": True,
                    "message": "Duplicate content detected during concurrent upload. Reference linked.",
                    "display_name": display_name,
                    "sha256_hash": sha256_hash,
                    "short_hash": shorten_hash(sha256_hash),
                    "file_size": file_size,
                    "formatted_size": format_bytes(file_size),
                    "storage_saved_bytes": file_size,
                    "formatted_saved": format_bytes(file_size),
                    "reference_id": file_ref.id,
                    "stored_file_id": existing_stored.id,
                    "storage_path": existing_stored.storage_path,
                }
            raise
        except Exception as e:
            db.session.rollback()
            # Compensation logic: if cloud upload succeeded but DB failed, remove orphan file from cloud
            if physical_upload_done:
                logger.warning(
                    f"Compensating transaction: removing orphan object {storage_path} from cloud storage."
                )
                FirebaseStorageService.delete_file(storage_path)
            logger.error(f"Failed to complete file upload pipeline: {e}")
            raise e
