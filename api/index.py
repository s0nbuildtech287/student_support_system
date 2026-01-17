"""
Vercel Serverless Entry Point
Wrapper cho Flask app để chạy trên Vercel
"""

import sys
import os

# Add parent directory to path để import được modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

# Vercel sẽ gọi biến này
handler = app

# For local testing
if __name__ == '__main__':
    app.run(debug=False)
