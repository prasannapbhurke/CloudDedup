import io
import pytest
from werkzeug.datastructures import FileStorage
from app import create_app
from app.extensions import db
from app.models.user import User
from app.services.deduplication_service import DeduplicationService
from app.services.statistics_service import StatisticsService


@pytest.fixture
def app_and_user():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        user = User(firebase_uid="stat_user_1", name="Stat Tester", email="stat@example.com")
        db.session.add(user)
        db.session.commit()
        yield app, user
        db.session.remove()
        db.drop_all()


def test_empty_account_statistics(app_and_user):
    """Test 11: Empty account returns zeroes with no division-by-zero error."""
    app, user = app_and_user
    with app.app_context():
        summary = StatisticsService.get_user_dashboard_summary(user.id)
        assert summary["total_files"] == 0
        assert summary["unique_files"] == 0
        assert summary["duplicate_references"] == 0
        assert summary["logical_bytes"] == 0
        assert summary["physical_bytes"] == 0
        assert summary["saved_bytes"] == 0
        assert summary["saving_percentage"] == 0.0


def test_storage_calculation_and_duplicate_groups(app_and_user):
    """Test 8 & 12: Verify exact formula calculations and duplicate group discovery."""
    app, user = app_and_user
    with app.app_context():
        # 10 MB simulated content (10,000,000 bytes)
        ten_mb_content = b"X" * 10000000
        # 5 MB simulated content (5,000,000 bytes)
        five_mb_content = b"Y" * 5000000

        # Upload 3 identical 10MB files under different names
        DeduplicationService.process_file_upload(
            user, FileStorage(stream=io.BytesIO(ten_mb_content), filename="assignment.pdf"), "assignment.pdf"
        )
        DeduplicationService.process_file_upload(
            user, FileStorage(stream=io.BytesIO(ten_mb_content), filename="cloud_assignment.pdf"), "cloud_assignment.pdf"
        )
        DeduplicationService.process_file_upload(
            user, FileStorage(stream=io.BytesIO(ten_mb_content), filename="final_assignment.pdf"), "final_assignment.pdf"
        )

        # Upload 1 separate 5MB file
        DeduplicationService.process_file_upload(
            user, FileStorage(stream=io.BytesIO(five_mb_content), filename="notes.pdf"), "notes.pdf"
        )

        # Verify Summary
        summary = StatisticsService.get_user_dashboard_summary(user.id)
        assert summary["total_files"] == 4
        assert summary["unique_files"] == 2
        assert summary["duplicate_references"] == 2

        # Logical = (3 * 10MB) + 5MB = 35MB
        assert summary["logical_bytes"] == 35000000
        # Physical = 10MB + 5MB = 15MB
        assert summary["physical_bytes"] == 15000000
        # Saved = 35MB - 15MB = 20MB
        assert summary["saved_bytes"] == 20000000
        # Saving % = (20 / 35) * 100 = 57.14%
        assert summary["saving_percentage"] == 57.14

        # Verify Duplicate Groups
        dup_groups = StatisticsService.get_duplicate_groups(user.id)
        # Exactly 1 duplicate group (the 10MB file with 3 refs; the 5MB file has only 1 ref so excluded)
        assert len(dup_groups) == 1
        group = dup_groups[0]
        assert group["reference_count"] == 3
        assert group["potential_savings_bytes"] == 20000000
