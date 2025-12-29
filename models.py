from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base model with common fields"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(BaseModel):
    """User model"""
    __tablename__ = 'users'
    
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    avatar = db.Column(db.String(500))
    year = db.Column(db.Integer)  # 1-4
    major = db.Column(db.String(255))
    gpa = db.Column(db.Float)
    career_goal = db.Column(db.String(500))
    status = db.Column(db.String(100), default="Đang học")
    is_active = db.Column(db.Boolean, default=True)
    
    # Study Preferences
    study_level = db.Column(db.String(50), default="Trung cấp")  # Sơ cấp, Trung cấp, Nâng cao
    study_goal = db.Column(db.String(100), default="Nâng cao kỹ năng")  # Nâng cao kỹ năng, Học để thi, Khám phá lĩnh vực mới
    study_style = db.Column(db.String(100), default="Video & Bài tập")  # Video & Bài tập, Video & Tài liệu, Tài liệu & Bài tập
    preferred_language = db.Column(db.String(50), default="Tiếng Việt")
    
    # Relationships
    enrollments = db.relationship('Enrollment', back_populates='user', cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', back_populates='user', cascade='all, delete-orphan')
    progress = db.relationship('Progress', back_populates='user', cascade='all, delete-orphan')
    roadmap_progress = db.relationship('RoadmapProgress', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name}>'

class Subject(BaseModel):
    """Subject model"""
    __tablename__ = 'subjects'
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(100))
    level = db.Column(db.String(50))  # Beginner, Intermediate, Advanced
    duration = db.Column(db.Integer)  # in hours
    image_url = db.Column(db.String(500))
    
    # Relationships
    enrollments = db.relationship('Enrollment', back_populates='subject', cascade='all, delete-orphan')
    lessons = db.relationship('Lesson', back_populates='subject', cascade='all, delete-orphan')
    outline_items = db.relationship('OutlineItem', back_populates='subject', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subject {self.name}>'

class Lesson(BaseModel):
    """Lesson model"""
    __tablename__ = 'lessons'
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer)
    content = db.Column(db.Text)
    
    # Relationships
    subject = db.relationship('Subject', back_populates='lessons')
    
    def __repr__(self):
        return f'<Lesson {self.title}>'

class Roadmap(BaseModel):
    """Roadmap model"""
    __tablename__ = 'roadmaps'
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    estimated_duration = db.Column(db.Integer)  # in weeks
    
    # Relationships
    subjects = db.relationship('RoadmapSubject', back_populates='roadmap', cascade='all, delete-orphan')
    progress = db.relationship('RoadmapProgress', back_populates='roadmap', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Roadmap {self.name}>'

class RoadmapSubject(BaseModel):
    """Association table for Roadmap and Subject"""
    __tablename__ = 'roadmap_subjects'
    
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmaps.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    order = db.Column(db.Integer)
    
    # Relationships
    roadmap = db.relationship('Roadmap', back_populates='subjects')
    subject = db.relationship('Subject')

class Enrollment(BaseModel):
    """Enrollment model - tracks user enrollment in subjects"""
    __tablename__ = 'enrollments'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    progress_percentage = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="In Progress")  # Completed, In Progress, Not Started
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='enrollments')
    subject = db.relationship('Subject', back_populates='enrollments')
    
    def __repr__(self):
        return f'<Enrollment {self.user.name} - {self.subject.name}>'

class Progress(BaseModel):
    """User progress model - tracks progress for each lesson"""
    __tablename__ = 'progress'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='progress')
    lesson = db.relationship('Lesson')
    
    def __repr__(self):
        return f'<Progress {self.user.name} - Lesson {self.lesson_id}>'

class RoadmapProgress(BaseModel):
    """Roadmap progress model"""
    __tablename__ = 'roadmap_progress'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmaps.id'), nullable=False)
    progress_percentage = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="In Progress")
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='roadmap_progress')
    roadmap = db.relationship('Roadmap', back_populates='progress')

class Feedback(BaseModel):
    """Feedback model"""
    __tablename__ = 'feedbacks'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 stars
    status = db.Column(db.String(50), default="New")  # New, In Progress, Resolved
    
    # Relationships
    user = db.relationship('User', back_populates='feedbacks')
    
    def __repr__(self):
        return f'<Feedback {self.subject}>'

class OutlineItem(BaseModel):
    """Subject outline item"""
    __tablename__ = 'outline_items'
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer)
    
    # Relationships
    subject = db.relationship('Subject', back_populates='outline_items')

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
