from flask import Blueprint, render_template, jsonify, g
from app.middleware.authentication import require_auth
from app.services.statistics_service import StatisticsService

statistics_bp = Blueprint("statistics", __name__)


@statistics_bp.route("/statistics")
def statistics_page():
    """Renders the comprehensive Storage Statistics and Analytics page."""
    return render_template("statistics.html")


@statistics_bp.route("/api/statistics/summary", methods=["GET"])
@require_auth
def statistics_summary_api():
    """Returns the primary storage statistics summary."""
    metrics = StatisticsService.get_user_dashboard_summary(g.current_user.id)
    return jsonify({"success": True, "metrics": metrics})


@statistics_bp.route("/api/statistics/trends", methods=["GET"])
@require_auth
def statistics_trends_api():
    """Returns upload activity trends over time for Chart.js line/bar charts."""
    trends = StatisticsService.get_upload_trends(g.current_user.id, days=14)
    return jsonify({"success": True, "trends": trends})


@statistics_bp.route("/api/statistics/file-types", methods=["GET"])
@require_auth
def statistics_file_types_api():
    """Returns storage distribution by file type for Chart.js doughnut chart."""
    distribution = StatisticsService.get_file_type_distribution(g.current_user.id)
    return jsonify({"success": True, "file_types": distribution})


@statistics_bp.route("/api/statistics/largest-files", methods=["GET"])
@require_auth
def statistics_largest_files_api():
    """Returns the user's largest referenced files."""
    largest = StatisticsService.get_largest_files(g.current_user.id, limit=5)
    return jsonify({"success": True, "largest_files": largest})
