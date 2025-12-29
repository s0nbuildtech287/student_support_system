# Study With AI - Copilot Instructions

## Project Overview

**Study With AI** is a Flask-based learning management system (LMS) for Vietnamese students. It provides subject browsing, learning roadmaps, progress tracking, user rankings, and personalized course recommendations.

### Core Architecture

- **Backend**: Flask with SQLAlchemy ORM + MySQL database
- **Frontend**: Jinja2 templates with vanilla JS for interactivity
- **Application Factory Pattern**: `create_app()` in [app.py](app.py) initializes Flask, config, database, and blueprints
- **Session-based Auth**: Uses `session['user_id']` for user authentication (no Flask-Login used despite import)

## Critical Data Flow

### User Learning Journey
1. **User Model** ([models.py](models.py#L17)): Stores profile (name, email, year, major, GPA, career_goal)
2. **Enrollment Model**: Tracks subject enrollment with progress_percentage (0-100)
3. **Progress Model**: Records individual lesson completion
4. **RoadmapProgress Model**: Tracks multi-subject learning paths

### Hybrid Data Architecture (⚠️ Important)
- **Subjects & Roadmaps**: Loaded from CSV files in `/data/` directory via service classes
  - `subject_service.py`: Loads subjects, filters by category/level, manages pagination
  - `roadmap_service.py`: Reads roadmap relationships, handles malformed CSV rows safely
- **User Data**: Stored in MySQL database via SQLAlchemy models
- **This hybrid approach** means subject/roadmap queries go through `services/`, while user actions hit the database

## Route Structure & Patterns

Each route file uses a consistent pattern:

```python
# routes/subject.py pattern
def get_current_user():
    """Get logged-in user from session - used in EVERY route file"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@subject_bp.route("/path")
def handler():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))  # Standard auth check
    # Handler logic
```

### Route Modules (in `/routes/`)
- **home.py**: Dashboard, statistics, recommendations
- **subject.py**: Subject listing, filtering, pagination
- **roadmap.py**: Learning paths, progress tracking
- **user.py**: Auth (login/register), profile updates, file uploads
- **ranking.py**: Leaderboards by category/year
- **feedback.py**: Course/lesson feedback collection

## Database Models & Relationships

**BaseModel** provides common fields: `id`, `created_at`, `updated_at` to all models.

### Key Relationships
- `User.enrollments` → `Enrollment.user` (cascade delete)
- `Subject.enrollments` → `Enrollment.subject`
- `User.progress` → `Progress.user` (lesson-level tracking)
- `Roadmap.subjects` → `RoadmapSubject` (association table with order)
- `User.roadmap_progress` → `RoadmapProgress`

## Developer Workflows

### Starting the Server
```bash
# From workspace root
source venv/bin/activate  # or venv\Scripts\activate on Windows
python run.py  # Uses FLASK_ENV, FLASK_HOST, FLASK_PORT from .env
```

### Database Setup
1. Create MySQL database: `CREATE DATABASE studywithai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
2. Load schema: Run `python init_db.py` (creates tables from models.py)
3. Seed data: Run `python seed.py` (loads CSV data into database)

### Configuration
- **Config layers**: [config.py](config.py) defines `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`
- **Environment**: `FLASK_ENV` env var determines which config loads
- **Database URI**: Built from env vars (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`)

## Project-Specific Conventions

### CSV Data Handling
- Subject/roadmap data originates in `/data/` CSVs, NOT the database (by design)
- Service functions handle malformed CSV rows gracefully (skip bad rows, don't crash)
- When adding new subject data, update CSVs first, then load via `seed.py`

### Pagination Pattern
```python
# Standard pagination in routes
page = request.args.get("page", 1, type=int)
per_page = 9  # Consistent page size for subjects
paginated = query.paginate(page=page, per_page=per_page, error_out=False)
```

### Authentication Guard
Every route checks `get_current_user()` first, redirects to login if missing. This is NOT using Flask-Login decorators.

### File Uploads
- Avatar uploads stored in `/static/images/`
- Allowed extensions: `{'png', 'jpg', 'jpeg', 'gif', 'avif', 'webp'}`
- Filenames secured with `secure_filename()` before saving

### Vietnamese Content
- UI messages often in Vietnamese ("Đang học", "Chưa đăng nhập", etc.)
- Maintain this localization when modifying templates/routes

## Dependencies & External Integration

- **Flask + extensions**: `flask-sqlalchemy` (ORM), `flask-login` (imported but unused), `flask-migrate`
- **Database**: `pymysql` driver (specified in SQLALCHEMY_DATABASE_URI)
- **Security**: `werkzeug` for password hashing (`generate_password_hash`, `check_password_hash`)
- **Environment**: `python-dotenv` for .env configuration

## Common Troubleshooting Patterns

1. **500 on auth routes**: Check `session['user_id']` is set after login (see `user.py`)
2. **Subject not showing**: Verify CSV data exists in `/data/subject_list.csv` and `seed.py` was run
3. **Database connection fails**: Validate MySQL is running and env vars match (see `.env` file)
4. **CSV parsing errors**: Services have built-in fault tolerance; check CSV headers match expected columns

## Files to Know

- **[app.py](app.py)**: Application factory and blueprint registration
- **[models.py](models.py)**: All SQLAlchemy model definitions
- **[config.py](config.py)**: Environment-based configuration
- **[services/](services/)**: CSV loading and business logic for subjects/roadmaps
- **[routes/](routes/)**: Blueprint handlers for each feature
- **[requirements.txt](requirements.txt)**: Python dependencies
