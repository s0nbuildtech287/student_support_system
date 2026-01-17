"""
Vercel Serverless Entry Point
Wrapper cho Flask app để chạy trên Vercel
"""

import sys
import os
import traceback

# Get the parent directory (root of project)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add to Python path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Change working directory to project root for relative imports
os.chdir(parent_dir)

try:
    # Import Flask app
    from app import app
    
    # Export for Vercel
    app = app
    
except Exception as e:
    # If import fails, create error app to show what went wrong
    from flask import Flask, jsonify
    
    error_app = Flask(__name__)
    error_message = str(e)
    error_traceback = traceback.format_exc()
    
    @error_app.route('/')
    def show_error():
        return jsonify({
            'error': 'Failed to import app',
            'message': error_message,
            'traceback': error_traceback,
            'sys_path': sys.path,
            'cwd': os.getcwd(),
            'parent_dir': parent_dir
        }), 500
    
    @error_app.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            'error': 'App failed to load',
            'message': error_message
        }), 500
    
    app = error_app

# For local testing
if __name__ == '__main__':
    app.run(debug=False)
