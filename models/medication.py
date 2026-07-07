"""
models/medication.py — Medication tracking SQLAlchemy model
"""

from datetime import datetime
from app_factory import db


class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(60))            # e.g., "500mg"
    frequency = db.Column(db.String(60))         # e.g., "Twice daily"
    timing = db.Column(db.String(120))           # e.g., "Morning 8am, Night 8pm"
    instructions = db.Column(db.Text)
    purpose = db.Column(db.String(200))
    prescribing_doctor = db.Column(db.String(120))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    refill_date = db.Column(db.String(20))

    # Adherence tracking
    total_doses = db.Column(db.Integer, default=0)
    taken_doses = db.Column(db.Integer, default=0)
    last_taken = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def adherence_pct(self):
        if self.total_doses and self.total_doses > 0:
            return round((self.taken_doses / self.total_doses) * 100, 1)
        return 0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "timing": self.timing,
            "purpose": self.purpose,
            "is_active": self.is_active,
            "adherence_pct": self.adherence_pct,
            "last_taken": str(self.last_taken) if self.last_taken else None,
            "refill_date": self.refill_date,
        }

    def __repr__(self):
        return f"<Medication {self.name} | Patient {self.patient_id}>"
