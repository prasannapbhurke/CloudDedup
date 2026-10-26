from flask import Blueprint, render_template, jsonify, g
from app.middleware.authentication import require_auth
from app.services.statistics_service import StatisticsService

duplicate_bp = Blueprint("duplicates", __name__)


@duplicate_bp.route("/duplicate-groups")
def duplicate_groups_page():
    """Renders the Duplicate Groups overview page."""
    return render_template("duplicate_groups.html")


@duplicate_bp.route("/duplicate-groups/<int:group_id>")
def duplicate_group_details_page(group_id):
    """Renders the detailed view of a specific duplicate group."""
    return render_template("duplicate_group_details.html", group_id=group_id)


@duplicate_bp.route("/api/duplicates", methods=["GET"])
@require_auth
def list_duplicate_groups_api():
    """
    Returns duplicate groups containing >= 2 references belonging to the current user.
    Never exposes other users' filenames or upload activities.
    """
    groups = StatisticsService.get_duplicate_groups(user_id=g.current_user.id)
    return jsonify({
        "success": True,
        "duplicate_groups": groups,
        "total_groups": len(groups),
    })


@duplicate_bp.route("/api/duplicates/<int:group_id>", methods=["GET"])
@require_auth
def get_duplicate_group_details_api(group_id):
    """
    Returns references within a duplicate group belonging to the current user.
    """
    group_details = StatisticsService.get_duplicate_group_details(
        user_id=g.current_user.id,
        group_id=group_id,
    )
    if not group_details:
        return jsonify({
            "success": False,
            "error": "Duplicate group not found or you have fewer than 2 references to it.",
        }), 404

    return jsonify({
        "success": True,
        "group": group_details,
    })
