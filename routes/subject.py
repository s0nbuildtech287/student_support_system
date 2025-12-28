from flask import Blueprint, render_template, request, abort
from services.subject_service import (
    load_all_subject_paginated,
    get_subject_by_uid
)

subject_bp = Blueprint("subject", __name__)

# hiển thị tất cả bài tập
@subject_bp.route("/subject")
def exercise():
    page = request.args.get("page", 1, type=int)
    data = load_all_subject_paginated(page=page, per_page=9)
    return render_template(
        "subject.html",
        exercises=data["subject_bp"],
        page=data["page"],
        total_pages=data["total_pages"]
    )

# # hiển thị chi tiết từng bài một
# @exercise_bp.route("/exercise/<int:uid>")
# def exercise_detail(uid):
#     exercise = get_exercise_by_uid(uid)

#     if not exercise:
#         abort(404)

#     return render_template("exercise_detail.html", exercise=exercise)
