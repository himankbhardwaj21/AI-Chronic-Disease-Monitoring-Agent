"""
wsgi.py — Production WSGI Entry Point for ChronicCare AI
Used by Gunicorn on Render, Railway, IBM Cloud Code Engine, etc.

Gunicorn command:
    gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT --timeout 120 --log-level info

Environment variables must be set in the hosting platform's dashboard.
Never pass secrets as command-line arguments.
"""

import os
from dotenv import load_dotenv

# Load .env file (no-op if env vars already set by the platform)
load_dotenv()

from app_factory import create_app      # noqa: E402
from config import configure_logging    # noqa: E402

# Use production config unless explicitly overridden
env = os.getenv("FLASK_ENV", "production")
app = create_app(env)
configure_logging(app)
