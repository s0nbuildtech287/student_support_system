from flask import Blueprint, render_template, request, abort
from services.exercise_service import (
    load_all_exercises_paginated,
    get_exercise_by_uid
)

exercise_bp = Blueprint("exercise", __name__)

# hiển thị tất cả bài tập
@exercise_bp.route("/exercise")
def exercise():
    page = request.args.get("page", 1, type=int)
    data = load_all_exercises_paginated(page=page, per_page=9)
    return render_template(
        "exercise.html",
        exercises=data["exercises"],
        page=data["page"],
        total_pages=data["total_pages"]
    )

# hiển thị chi tiết từng bài một
@exercise_bp.route("/exercise/<int:uid>")
def exercise_detail(uid):
    exercise = get_exercise_by_uid(uid)

    if not exercise:
        abort(404)

    return render_template("exercise_detail.html", exercise=exercise)
