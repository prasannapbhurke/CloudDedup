import io
import pytest
from werkzeug.datastructures import FileStorage
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.stored_file import StoredFile
from app.models.file_reference import FileReference
from app.services.deduplication_service import DeduplicationService


@pytest.fixture
def app_and_db():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        # Create test user
        user = User(firebase_uid="test_uid_123", name="Test Student", email="test@clouddedup.com")
        db.session.add(user)
        db.session.commit()
        yield app, db, user
        db.session.remove()
        db.drop_all()


def test_new_upload_workflow(app_and_db):
    """Test 1: Upload a brand new file."""
    app, database, user = app_and_db
    with app.app_context():
        file_bytes = b"Sample unique assignment document content"
        storage = FileStorage(stream=io.BytesIO(file_bytes), filename="assignment.pdf", content_type="application/pdf")

        result = DeduplicationService.process_file_upload(user, storage, "assignment.pdf")

        assert result["success"] is True
        assert result["is_duplicate"] is False
        assert StoredFile.query.count() == 1
        assert FileReference.query.count() == 1

        stored = StoredFile.query.first()
        ref = FileReference.query.first()
        assert ref.stored_file_id == stored.id
        assert ref.display_name == "assignment.pdf"
        assert stored.reference_count == 1


def test_duplicate_upload_different_filename(app_and_db):
    """Test 2: Upload identical content under different filenames (assignment.pdf then cloud_assignment.pdf)."""
    app, database, user = app_and_db
    with app.app_context():
        identical_content = b"Exact identical 10MB byte stream content"

        # 1st Upload
        file1 = FileStorage(stream=io.BytesIO(identical_content), filename="assignment.pdf")
        res1 = DeduplicationService.process_file_upload(user, file1, "assignment.pdf")
        assert res1["is_duplicate"] is False

        # 2nd Upload with DIFFERENT filename
        file2 = FileStorage(stream=io.BytesIO(identical_content), filename="cloud_assignment.pdf")
        res2 = DeduplicationService.process_file_upload(user, file2, "cloud_assignment.pdf")

        # Verifications
        assert res2["success"] is True
        assert res2["is_duplicate"] is True
        assert res2["storage_saved_bytes"] == len(identical_content)

        # Database state: exactly 1 stored file, 2 references
        assert StoredFile.query.count() == 1
        assert FileReference.query.count() == 2

        stored = StoredFile.query.first()
        assert stored.reference_count == 2

        refs = FileReference.query.all()
        ref_names = [r.display_name for r in refs]
        assert "assignment.pdf" in ref_names
        assert "cloud_assignment.pdf" in ref_names


def test_modified_content_creates_new_object(app_and_db):
    """Test 3: Upload modified content; verify separate stored file is created."""
    app, database, user = app_and_db
    with app.app_context():
        content_v1 = b"Assignment Draft Version 1.0"
        content_v2 = b"Assignment Draft Version 2.0 with updates"

        file1 = FileStorage(stream=io.BytesIO(content_v1), filename="draft.pdf")
        DeduplicationService.process_file_upload(user, file1, "draft.pdf")

        file2 = FileStorage(stream=io.BytesIO(content_v2), filename="draft_v2.pdf")
        res2 = DeduplicationService.process_file_upload(user, file2, "draft_v2.pdf")

        assert res2["is_duplicate"] is False
        assert StoredFile.query.count() == 2
        assert FileReference.query.count() == 2
