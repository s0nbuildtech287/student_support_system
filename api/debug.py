"""
Minimal Vercel Entry Point for Debugging
"""

import sys
import os

# Setup paths
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
os.chdir(parent_dir)

# Try to import and show errors
try:
    from flask import Flask
    from config import Config
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    @app.route('/')
    def index():
        return {
            'status': 'ok',
            'message': 'Flask app is running',
            'env_check': {
                'POSTGRES_URL': 'set' if os.getenv('POSTGRES_URL') else 'missing',
                'SECRET_KEY': 'set' if Config.SECRET_KEY else 'missing',
                'GROQ_API_KEY': 'set' if os.getenv('GROQ_API_KEY') else 'missing'
            }
        }
    
    @app.route('/test')
    def test():
        return {'message': 'Test route works'}
        
    # Export for Vercel
    app = app
    
except Exception as e:
    import traceback
    
    # Create error app
    error_app = Flask(__name__)
    
    @error_app.route('/')
    def error():
        return {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'sys_path': sys.path,
            'cwd': os.getcwd()
        }, 500
    
    app = error_app
