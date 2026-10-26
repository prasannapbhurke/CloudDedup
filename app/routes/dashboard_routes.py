from flask import Blueprint, render_template, redirect, url_for, jsonify, g
from app.middleware.authentication import require_auth
from app.models.upload_event import UploadEvent
from app.models.stored_file import StoredFile
from app.services.statistics_service import StatisticsService
from app.utils.file_helpers import format_bytes, shorten_hash, get_file_type_category, get_file_icon_class

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    """Root redirect to dashboard."""
    return redirect(url_for("dashboard.dashboard_page"))


@dashboard_bp.route("/dashboard")
def dashboard_page():
    """Renders the primary storage optimization dashboard."""
    return render_template("dashboard.html")


@dashboard_bp.route("/settings")
def settings_page():
    """Renders user profile and preferences settings page."""
    return render_template("settings.html")


@dashboard_bp.route("/api/dashboard/summary", methods=["GET"])
@require_auth
def dashboard_summary_api():
    """
    Returns the 7 primary dashboard metrics calculated live from MySQL,
    along with recent upload activity for the current user.
    """
    user_id = g.current_user.id
    metrics = StatisticsService.get_user_dashboard_summary(user_id)

    # Fetch 5 most recent upload events for this user
    recent_events = (
        UploadEvent.query.filter_by(user_id=user_id)
        .order_by(UploadEvent.created_at.desc())
        .limit(5)
        .all()
    )

    recent_list = []
    for ev in recent_events:
        recent_list.append({
            "id": ev.id,
            "filename": ev.original_filename,
            "file_size": ev.file_size,
            "formatted_size": format_bytes(ev.file_size),
            "sha256_hash": ev.sha256_hash,
            "short_hash": shorten_hash(ev.sha256_hash),
            "event_type": ev.event_type,
            "is_duplicate": (ev.event_type == "duplicate_detected"),
            "event_label": "Duplicate Content" if ev.event_type == "duplicate_detected" else "New File Upload",
            "created_at": ev.created_at.strftime("%Y-%m-%d %H:%M:%S") if ev.created_at else "",
            "category": get_file_type_category(ev.original_filename),
            "icon_class": get_file_icon_class(ev.original_filename),
        })

    return jsonify({
        "success": True,
        "metrics": metrics,
        "recent_uploads": recent_list,
        "user": g.current_user.to_dict(),
    })
