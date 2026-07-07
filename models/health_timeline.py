"""
models/health_timeline.py — Health event timeline model
Records chronological health events for Feature 5.
"""

from datetime import datetime
from app_factory import db


class HealthTimeline(db.Model):
    __tablename__ = "health_timeline"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    # Event classification
    event_type = db.Column(db.String(40), nullable=False)
    # Types: medication_taken | medication_missed | blood_sugar_change |
    #        bp_change | doctor_visit | exercise | sleep_record |
    #        weight_change | risk_change | ai_recommendation | symptom | mood

    event_category = db.Column(db.String(20))   # health | medication | lifestyle | ai
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    value = db.Column(db.String(60))             # e.g. "135 mg/dL", "7.5 hrs"
    previous_value = db.Column(db.String(60))    # for change events
    icon = db.Column(db.String(40))              # Bootstrap icon class
    color = db.Column(db.String(20))             # Bootstrap color name
    severity = db.Column(db.String(20))          # info | success | warning | danger

    # Linked record
    health_record_id = db.Column(db.Integer, db.ForeignKey("health_records.id"), nullable=True)

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_category": self.event_category,
            "title": self.title,
            "description": self.description,
            "value": self.value,
            "previous_value": self.previous_value,
            "icon": self.icon,
            "color": self.color,
            "severity": self.severity,
            "recorded_at": self.recorded_at.strftime("%Y-%m-%d %H:%M") if self.recorded_at else None,
            "recorded_date": self.recorded_at.strftime("%b %d, %Y") if self.recorded_at else None,
            "recorded_time": self.recorded_at.strftime("%I:%M %p") if self.recorded_at else None,
        }

    def __repr__(self):
        return f"<Timeline [{self.event_type}] {self.title}>"
