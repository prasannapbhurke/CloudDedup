from datetime import datetime, timedelta, timezone
from collections import defaultdict
from sqlalchemy import func, distinct
from app.extensions import db
from app.models.stored_file import StoredFile
from app.models.file_reference import FileReference
from app.models.upload_event import UploadEvent
from app.utils.file_helpers import format_bytes, shorten_hash, get_file_type_category, get_file_icon_class


class StatisticsService:
    """
    Analytics & Storage Optimization Service.
    Calculates user-isolated metrics, duplicate groups, and Chart.js datasets.
    """

    @classmethod
    def get_user_dashboard_summary(cls, user_id):
        """
        Calculates the primary 7 metric cards strictly per specification:
        1. Total Files
        2. Unique Files
        3. Duplicate References
        4. Logical Storage (Bytes & Formatted)
        5. Physical Storage (Bytes & Formatted)
        6. Storage Saved (Bytes & Formatted)
        7. Saving Percentage
        """
        # 1. Total files for user
        total_files = FileReference.query.filter_by(user_id=user_id).count()

        if total_files == 0:
            return {
                "total_files": 0,
                "unique_files": 0,
                "duplicate_references": 0,
                "logical_bytes": 0,
                "logical_formatted": "0 B",
                "physical_bytes": 0,
                "physical_formatted": "0 B",
                "saved_bytes": 0,
                "saved_formatted": "0 B",
                "saving_percentage": 0.0,
            }

        # 2. Unique files (distinct stored_file_id referenced by user)
        unique_files = (
            db.session.query(func.count(distinct(FileReference.stored_file_id)))
            .filter(FileReference.user_id == user_id)
            .scalar()
            or 0
        )

        # 3. Duplicate references within user's files
        duplicate_references = max(0, total_files - unique_files)

        # 4. Logical Storage = sum of sizes of ALL user references
        logical_bytes = (
            db.session.query(func.sum(StoredFile.file_size))
            .join(FileReference, FileReference.stored_file_id == StoredFile.id)
            .filter(FileReference.user_id == user_id)
            .scalar()
            or 0
        )

        # 5. Physical Storage = sum of sizes of DISTINCT stored objects referenced by user
        # We query the distinct stored_files for this user
        distinct_ids_subquery = (
            db.session.query(FileReference.stored_file_id)
            .filter(FileReference.user_id == user_id)
            .distinct()
        )
        physical_bytes = (
            db.session.query(func.sum(StoredFile.file_size))
            .filter(StoredFile.id.in_(distinct_ids_subquery))
            .scalar()
            or 0
        )

        # 6. Storage Saved
        saved_bytes = max(0, logical_bytes - physical_bytes)

        # 7. Saving Percentage
        saving_percentage = (saved_bytes / logical_bytes * 100.0) if logical_bytes > 0 else 0.0

        return {
            "total_files": total_files,
            "unique_files": unique_files,
            "duplicate_references": duplicate_references,
            "logical_bytes": int(logical_bytes),
            "logical_formatted": format_bytes(logical_bytes),
            "physical_bytes": int(physical_bytes),
            "physical_formatted": format_bytes(physical_bytes),
            "saved_bytes": int(saved_bytes),
            "saved_formatted": format_bytes(saved_bytes),
            "saving_percentage": round(saving_percentage, 2),
        }

    @classmethod
    def get_duplicate_groups(cls, user_id):
        """
        Retrieves all duplicate groups for the current user.
        A duplicate group contains >= 2 references pointing to the same StoredFile.
        Groups with only 1 reference are excluded.
        """
        # Find stored_files where user has >= 2 references
        grouped = (
            db.session.query(
                FileReference.stored_file_id,
                func.count(FileReference.id).label("ref_count"),
            )
            .filter(FileReference.user_id == user_id)
            .group_by(FileReference.stored_file_id)
            .having(func.count(FileReference.id) >= 2)
            .all()
        )

        groups_data = []
        for stored_file_id, ref_count in grouped:
            stored = db.session.get(StoredFile, stored_file_id)
            if not stored:
                continue

            # Fetch all user's references in this group
            user_refs = (
                FileReference.query.filter_by(user_id=user_id, stored_file_id=stored_file_id)
                .order_by(FileReference.uploaded_at.asc())
                .all()
            )

            original_filename = user_refs[0].display_name if user_refs else "Unknown"
            potential_savings_bytes = stored.file_size * (ref_count - 1)

            groups_data.append({
                "group_id": stored.id,
                "sha256_hash": stored.sha256_hash,
                "short_hash": shorten_hash(stored.sha256_hash),
                "file_size": stored.file_size,
                "formatted_size": format_bytes(stored.file_size),
                "reference_count": ref_count,
                "duplicate_count": ref_count - 1,
                "original_filename": original_filename,
                "potential_savings_bytes": potential_savings_bytes,
                "formatted_savings": format_bytes(potential_savings_bytes),
                "category": get_file_type_category(original_filename),
                "icon_class": get_file_icon_class(original_filename),
            })

        # Sort groups by highest potential savings first
        groups_data.sort(key=lambda g: g["potential_savings_bytes"], reverse=True)
        return groups_data

    @classmethod
    def get_duplicate_group_details(cls, user_id, group_id):
        """
        Fetches detailed references belonging to a specific duplicate group for this user.
        Strictly limits to the current user's file references.
        """
        stored = db.session.get(StoredFile, group_id)
        if not stored:
            return None

        # Fetch only references belonging to THIS user
        user_refs = (
            FileReference.query.filter_by(user_id=user_id, stored_file_id=group_id)
            .order_by(FileReference.uploaded_at.asc())
            .all()
        )

        if not user_refs or len(user_refs) < 2:
            return None

        ref_list = []
        for index, ref in enumerate(user_refs):
            ref_list.append({
                "id": ref.id,
                "display_name": ref.display_name,
                "file_size": stored.file_size,
                "formatted_size": format_bytes(stored.file_size),
                "uploaded_at": ref.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if ref.uploaded_at else "",
                "is_duplicate": ref.is_duplicate,
                "status_label": "Earliest (Original)" if index == 0 else "Duplicate",
                "category": get_file_type_category(ref.display_name),
                "icon_class": get_file_icon_class(ref.display_name),
            })

        potential_savings = stored.file_size * (len(user_refs) - 1)

        return {
            "group_id": stored.id,
            "sha256_hash": stored.sha256_hash,
            "short_hash": shorten_hash(stored.sha256_hash),
            "file_size": stored.file_size,
            "formatted_size": format_bytes(stored.file_size),
            "reference_count": len(user_refs),
            "potential_savings_bytes": potential_savings,
            "formatted_savings": format_bytes(potential_savings),
            "references": ref_list,
        }

    @classmethod
    def get_file_type_distribution(cls, user_id):
        """
        Computes file-type breakdown for Chart.js (counts, logical bytes, physical bytes).
        """
        user_refs = (
            db.session.query(FileReference, StoredFile)
            .join(StoredFile, FileReference.stored_file_id == StoredFile.id)
            .filter(FileReference.user_id == user_id)
            .all()
        )

        counts = defaultdict(int)
        logical_sizes = defaultdict(int)

        for ref, stored in user_refs:
            cat = get_file_type_category(ref.display_name)
            counts[cat] += 1
            logical_sizes[cat] += stored.file_size

        labels = sorted(counts.keys())
        data_counts = [counts[l] for l in labels]
        data_sizes = [logical_sizes[l] for l in labels]
        formatted_sizes = [format_bytes(logical_sizes[l]) for l in labels]

        return {
            "labels": labels,
            "counts": data_counts,
            "sizes_bytes": data_sizes,
            "formatted_sizes": formatted_sizes,
        }

    @classmethod
    def get_upload_trends(cls, user_id, days=14):
        """
        Aggregates upload events over the last N days for trend visualization.
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days - 1)
        events = (
            UploadEvent.query.filter(
                UploadEvent.user_id == user_id,
                UploadEvent.created_at >= start_date,
            )
            .order_by(UploadEvent.created_at.asc())
            .all()
        )

        # Generate date range list
        date_map = {}
        for i in range(days):
            day = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            date_map[day] = {"new": 0, "duplicate": 0}

        for ev in events:
            day_str = ev.created_at.strftime("%Y-%m-%d")
            if day_str in date_map:
                if ev.event_type == "new_upload":
                    date_map[day_str]["new"] += 1
                else:
                    date_map[day_str]["duplicate"] += 1

        labels = sorted(date_map.keys())
        new_uploads = [date_map[d]["new"] for d in labels]
        duplicates = [date_map[d]["duplicate"] for d in labels]

        return {
            "labels": labels,
            "new_uploads": new_uploads,
            "duplicate_detected": duplicates,
        }

    @classmethod
    def get_largest_files(cls, user_id, limit=5):
        """
        Returns the top largest stored objects referenced by this user.
        """
        distinct_stored_ids = (
            db.session.query(FileReference.stored_file_id)
            .filter(FileReference.user_id == user_id)
            .distinct()
        )

        largest = (
            StoredFile.query.filter(StoredFile.id.in_(distinct_stored_ids))
            .order_by(StoredFile.file_size.desc())
            .limit(limit)
            .all()
        )

        result = []
        for sf in largest:
            # Get one user reference display name
            sample_ref = (
                FileReference.query.filter_by(user_id=user_id, stored_file_id=sf.id)
                .first()
            )
            name = sample_ref.display_name if sample_ref else "Unknown"
            result.append({
                "id": sf.id,
                "display_name": name,
                "file_size": sf.file_size,
                "formatted_size": format_bytes(sf.file_size),
                "short_hash": shorten_hash(sf.sha256_hash),
                "category": get_file_type_category(name),
                "icon_class": get_file_icon_class(name),
            })

        return result
