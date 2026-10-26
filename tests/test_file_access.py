import io
import pytest
from werkzeug.datastructures import FileStorage
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.stored_file import StoredFile
from app.models.file_reference import FileReference
from app.services.deduplication_service import DeduplicationService
from app.services.file_management_service import FileManagementService


@pytest.fixture
def multi_user_setup():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        user_a = User(firebase_uid="uid_alice", name="Alice", email="alice@example.com")
        user_b = User(firebase_uid="uid_bob", name="Bob", email="bob@example.com")
        db.session.add_all([user_a, user_b])
        db.session.commit()
        yield app, user_a, user_b
        db.session.remove()
        db.drop_all()


def test_multi_user_deduplication_and_isolation(multi_user_setup):
    """Test 4 & 9: Multi-user shared storage with strict reference isolation."""
    app, user_a, user_b = multi_user_setup
    with app.app_context():
        shared_content = b"Shared cloud lab manual document"

        # User A uploads
        file_a = FileStorage(stream=io.BytesIO(shared_content), filename="alice_manual.pdf")
        res_a = DeduplicationService.process_file_upload(user_a, file_a, "alice_manual.pdf")

        # User B uploads exact same content under different filename
        file_b = FileStorage(stream=io.BytesIO(shared_content), filename="bob_manual.pdf")
        res_b = DeduplicationService.process_file_upload(user_b, file_b, "bob_manual.pdf")

        # Exactly 1 physical object exists in cloud
        assert StoredFile.query.count() == 1
        assert StoredFile.query.first().reference_count == 2

        # User A only sees alice_manual.pdf
        files_a = FileManagementService.get_user_files(user_a.id)["files"]
        assert len(files_a) == 1
        assert files_a[0]["display_name"] == "alice_manual.pdf"

        # User B only sees bob_manual.pdf
        files_b = FileManagementService.get_user_files(user_b.id)["files"]
        assert len(files_b) == 1
        assert files_b[0]["display_name"] == "bob_manual.pdf"

        # Unauthorized access attempt: Bob attempts to download Alice's reference
        with pytest.raises(PermissionError):
            FileManagementService.download_file_reference(user_id=user_b.id, reference_id=res_a["reference_id"])


def test_reference_deletion_lifecycle(multi_user_setup):
    """Test 6 & 7: Deleting one reference retains physical object; deleting last reference purges it."""
    app, user_a, user_b = multi_user_setup
    with app.app_context():
        content = b"Important course syllabus file"

        # Upload for User A
        res_a = DeduplicationService.process_file_upload(
            user_a, FileStorage(stream=io.BytesIO(content), filename="syllabus_a.pdf"), "syllabus_a.pdf"
        )
        # Upload duplicate for User A
        res_a2 = DeduplicationService.process_file_upload(
            user_a, FileStorage(stream=io.BytesIO(content), filename="syllabus_copy.pdf"), "syllabus_copy.pdf"
        )

        assert StoredFile.query.count() == 1
        assert FileReference.query.count() == 2

        # Case 1 (Test 6): Delete one duplicate reference
        del_result1 = FileManagementService.delete_file_reference(user_a.id, res_a2["reference_id"])
        assert del_result1["physical_purged"] is False
        assert StoredFile.query.count() == 1
        assert FileReference.query.count() == 1

        # Case 2 (Test 7): Delete the final remaining reference
        del_result2 = FileManagementService.delete_file_reference(user_a.id, res_a["reference_id"])
        assert del_result2["physical_purged"] is True
        assert StoredFile.query.count() == 0
        assert FileReference.query.count() == 0
