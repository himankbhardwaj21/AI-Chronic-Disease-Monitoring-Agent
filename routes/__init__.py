"""routes/__init__.py — ChronicCare AI routes package"""
from .dashboard import dashboard_bp
from .patients import patients_bp
from .health_data import health_data_bp
from .agents import agents_bp
from .chat import chat_bp
from .reports import reports_bp

__all__ = [
    "dashboard_bp",
    "patients_bp",
    "health_data_bp",
    "agents_bp",
    "chat_bp",
    "reports_bp",
]
