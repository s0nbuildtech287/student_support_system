"""Database seed data"""
from models import db, User, Subject, Lesson, Roadmap, RoadmapSubject, OutlineItem

def seed_database():
    """Seed initial data"""
    
    # Clear existing data
    db.session.query(OutlineItem).delete()
    db.session.query(RoadmapSubject).delete()
    db.session.query(Roadmap).delete()
    db.session.query(Lesson).delete()
    db.session.query(Subject).delete()
    db.session.query(User).delete()
    db.session.commit()
    
    # Create sample user
    user = User(
        name="Khang Nguyen",
        email="khang@example.com",
        password="hashed_password",
        age=25,
        avatar="/static/images/avatar.jpg",
        year=3,
        major="Công nghệ thông tin",
        gpa=3.75,
        career_goal="Software Engineer",
        status="Đang học"
    )
    db.session.add(user)
    
    # Create subjects
    subjects_data = [
        {
            "name": "Python Programming",
            "code": "CS101",
            "category": "Programming",
            "level": "Beginner",
            "duration": 40,
            "description": "Learn Python from basics to advanced"
        },
        {
            "name": "Web Development",
            "code": "CS201",
            "category": "Web",
            "level": "Intermediate",
            "duration": 60,
            "description": "Master web development with Python and JavaScript"
        },
        {
            "name": "Data Science",
            "code": "DS101",
            "category": "Data Science",
            "level": "Intermediate",
            "duration": 50,
            "description": "Data analysis and visualization"
        },
        {
            "name": "Database Design",
            "code": "CS301",
            "category": "Database",
            "level": "Advanced",
            "duration": 45,
            "description": "Design and implement databases"
        },
        {
            "name": "Mobile Development",
            "code": "CS401",
            "category": "Mobile",
            "level": "Advanced",
            "duration": 55,
            "description": "Build mobile applications"
        }
    ]
    
    subjects = []
    for data in subjects_data:
        subject = Subject(**data)
        db.session.add(subject)
        subjects.append(subject)
    
    db.session.flush()
    
    # Create lessons for first subject
    if subjects:
        lessons_data = [
            {"subject_id": subjects[0].id, "title": "Introduction to Python", "order": 1, "description": "Learn Python basics"},
            {"subject_id": subjects[0].id, "title": "Variables and Data Types", "order": 2, "description": "Understand Python data types"},
            {"subject_id": subjects[0].id, "title": "Control Flow", "order": 3, "description": "If statements and loops"},
        ]
        
        for data in lessons_data:
            lesson = Lesson(**data)
            db.session.add(lesson)
    
    # Create outline items for subjects
    outline_items = [
        {
            "subject_id": subjects[0].id,
            "title": "Module 1: Python Basics",
            "description": "Introduction to Python programming",
            "order": 1
        },
        {
            "subject_id": subjects[0].id,
            "title": "Module 2: Object-Oriented Programming",
            "description": "Classes and objects in Python",
            "order": 2
        },
        {
            "subject_id": subjects[1].id,
            "title": "Module 1: HTML & CSS",
            "description": "Frontend basics",
            "order": 1
        },
        {
            "subject_id": subjects[1].id,
            "title": "Module 2: JavaScript",
            "description": "Dynamic web pages",
            "order": 2
        }
    ]
    
    for data in outline_items:
        item = OutlineItem(**data)
        db.session.add(item)
    
    db.session.flush()
    
    # Create roadmaps
    roadmaps_data = [
        {
            "name": "Full Stack Web Development",
            "description": "Complete path to become a full stack developer",
            "estimated_duration": 24
        },
        {
            "name": "Data Science Professional",
            "description": "Path to become a data science professional",
            "estimated_duration": 20
        },
        {
            "name": "Cloud Developer",
            "description": "Learn cloud development and deployment",
            "estimated_duration": 16
        }
    ]
    
    roadmaps = []
    for data in roadmaps_data:
        roadmap = Roadmap(**data)
        db.session.add(roadmap)
        roadmaps.append(roadmap)
    
    db.session.flush()
    
    # Create roadmap subjects
    if roadmaps and len(subjects) >= 2:
        roadmap_subjects = [
            {"roadmap_id": roadmaps[0].id, "subject_id": subjects[0].id, "order": 1},
            {"roadmap_id": roadmaps[0].id, "subject_id": subjects[1].id, "order": 2},
            {"roadmap_id": roadmaps[1].id, "subject_id": subjects[2].id, "order": 1},
            {"roadmap_id": roadmaps[2].id, "subject_id": subjects[3].id, "order": 1},
        ]
        
        for data in roadmap_subjects:
            rs = RoadmapSubject(**data)
            db.session.add(rs)
    
    db.session.commit()
    print("✅ Database seeded successfully!")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()
