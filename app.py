import os
from flask import Flask, redirect
from dotenv import load_dotenv
from config import config
from models import db, init_db
from routes.subject import subject_bp
from routes.home import home_bp
from routes.ranking import ranking_bp
from routes.user import user_bp
from routes.roadmap import roadmap_bp
from routes.feedback import feedback_bp

load_dotenv()

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(subject_bp)
    app.register_blueprint(ranking_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(feedback_bp)
    
    # Default route
    @app.route("/")
    def index():
        return redirect("/home")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)