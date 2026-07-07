"""
models/alert.py — AI-generated health alert SQLAlchemy model
"""

from datetime import datetime
from app_factory import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    # Alert Details
    alert_type = db.Column(db.String(50))        # vital / medication / lifestyle / emergency
    severity = db.Column(db.String(20))          # Info / Warning / Critical / Emergency
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    recommended_action = db.Column(db.Text)
    triggered_by = db.Column(db.String(100))     # which metric triggered it
    triggered_value = db.Column(db.String(50))   # the value that triggered it

    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "recommended_action": self.recommended_action,
            "triggered_by": self.triggered_by,
            "triggered_value": self.triggered_value,
            "is_read": self.is_read,
            "is_resolved": self.is_resolved,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
        }

    def __repr__(self):
        return f"<Alert [{self.severity}] {self.title}>"
