from flask import Blueprint, render_template, request, abort
from services.subject_service import (
    load_all_subject_paginated,
    get_subject_by_uid
)
from routes.user import CURRENT_USER

subject_bp = Blueprint("subject", __name__)

# Danh sách môn học
@subject_bp.route("/subject")
def subject_list():
    page = request.args.get("page", 1, type=int)

    category = request.args.get("category", "").strip()
    level = request.args.get("level", "").strip()

    data = load_all_subject_paginated(
        page=page,
        per_page=9,
        category=category,
        level=level
    )

    return render_template(
        "subject.html",
        subjects=data["subjects"],
        page=data["page"],
        total_pages=data["total_pages"],

        # để giữ trạng thái form
        categories=data["categories"],
        selected_category=category,
        selected_level=level,
        keyword="",   # bỏ qua keyword
        user=CURRENT_USER
    )



# Chi tiết môn học
@subject_bp.route("/subject/<int:uid>")
def subject_detail(uid):
    subject = get_subject_by_uid(uid)

    if not subject:
        abort(404)

    return render_template(
        "subject_detail.html",
        subject=subject,
        user=CURRENT_USER
    )
