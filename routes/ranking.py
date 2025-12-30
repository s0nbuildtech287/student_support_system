from flask import Blueprint, render_template
from routes.user import CURRENT_USER

ranking_bp = Blueprint("ranking", __name__)

@ranking_bp.route("/ranking")
def ranking():

    roadmap_labels = [
      "Backend Developer", "Data Analyst", "AI Engineer", "Frontend Developer",
      "DevOps Engineer", "Cyber Security", "Mobile Developer",
      "Business Analyst", "Digital Marketing", "Cloud Engineer"
    ]

    roadmap_values = [520, 480, 450, 420, 390, 360, 330, 300, 280, 260]

    subject_labels = [
      "Python", "SQL", "Data Structures", "Machine Learning", "Java",
      "Web API", "Statistics", "Cloud Basics", "AI Fundamentals", "Linux"
    ]

    subject_values = [890, 840, 800, 760, 720, 690, 650, 620, 600, 580]

    top_completed = [
      {"name": "Nguyễn Văn A", "completed": 48},
      {"name": "Trần Thị B", "completed": 46},
      {"name": "Lê Văn C", "completed": 44},
      {"name": "Phạm Thị D", "completed": 42},
      {"name": "Hoàng Văn E", "completed": 41},
      {"name": "Đỗ Minh F", "completed": 40},
      {"name": "Bùi Thanh G", "completed": 39},
      {"name": "Vũ Quốc H", "completed": 38},
      {"name": "Ngô Thị I", "completed": 37},
      {"name": "Đinh Văn K", "completed": 36},
    ]

    top_score = [
      {"name": "Trần Minh Khang", "score": 985},
      {"name": "Nguyễn Hoàng Long", "score": 972},
      {"name": "Lê Thị Mai", "score": 960},
      {"name": "Phạm Quốc Huy", "score": 955},
      {"name": "Đặng Minh Tâm", "score": 948},
      {"name": "Võ Thanh Sơn", "score": 940},
      {"name": "Nguyễn Thu Hà", "score": 935},
      {"name": "Trịnh Quang Dũng", "score": 930},
      {"name": "Hoàng Ngọc Anh", "score": 925},
      {"name": "Bùi Đức Thịnh", "score": 920},
    ]

    return render_template(
        "ranking.html",
        roadmap_labels=roadmap_labels,
        roadmap_values=roadmap_values,
        subject_labels=subject_labels,
        subject_values=subject_values,
        top_completed=top_completed,
        top_score=top_score,
        user=CURRENT_USER
    )
