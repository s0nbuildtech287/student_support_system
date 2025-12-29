#!/usr/bin/env python
"""Run the application"""

import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

if __name__ == "__main__":
    app = create_app()
    
    host = os.getenv('FLASK_HOST', 'localhost')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    
    print(f"\n🚀 Starting Study With AI")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
