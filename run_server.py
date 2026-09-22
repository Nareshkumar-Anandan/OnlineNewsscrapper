"""
Production Server Runner
Uses Waitress (Cross-Platform / Windows / Linux) or Gunicorn for production hosting
"""
import os
import sys

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, FRONTEND_DIR, API_KEY

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    threads = int(os.environ.get('THREADS', 4))
    
    print("\n" + "="*60)
    print(" 🚀 Starting Production Server with Waitress WSGI")
    print("="*60)
    print(f" Serving on       : http://{host}:{port}")
    print(f" Frontend Root    : {FRONTEND_DIR}")
    print(f" API Key Status   : {'Configured' if API_KEY else 'Fallback Mode (No Key)'}")
    print(f" Worker Threads   : {threads}")
    print("="*60 + "\n")
    
    try:
        from waitress import serve
        serve(app, host=host, port=port, threads=threads)
    except ImportError:
        print("[!] Waitress not installed, falling back to Flask development server...")
        app.run(host=host, port=port, debug=False)
