"""
models/health_record.py — Health vitals and daily metrics SQLAlchemy model
"""

from datetime import datetime
from app_factory import db


class HealthRecord(db.Model):
    __tablename__ = "health_records"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Vital Signs
    blood_glucose = db.Column(db.Float)          # mg/dL
    systolic_bp = db.Column(db.Integer)          # mmHg
    diastolic_bp = db.Column(db.Integer)         # mmHg
    heart_rate = db.Column(db.Integer)           # bpm
    oxygen_saturation = db.Column(db.Float)      # %
    body_temperature = db.Column(db.Float)       # °C
    pulse = db.Column(db.Integer)                # bpm
    respiratory_rate = db.Column(db.Integer)     # breaths/min

    # Body Metrics
    weight_kg = db.Column(db.Float)
    bmi = db.Column(db.Float)

    # Lifestyle Metrics
    sleep_hours = db.Column(db.Float)
    water_intake_liters = db.Column(db.Float)
    exercise_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    steps_count = db.Column(db.Integer)

    # Subjective Metrics
    stress_level = db.Column(db.Integer)         # 1-10
    pain_level = db.Column(db.Integer)           # 1-10
    mood = db.Column(db.String(30))              # Great/Good/Fair/Poor/Terrible
    symptoms = db.Column(db.Text)               # comma-separated
    notes = db.Column(db.Text)

    # AI-Generated Scores (computed and stored)
    health_score = db.Column(db.Float)           # 0-100
    risk_level = db.Column(db.String(20))        # Low/Medium/High/Critical
    ai_summary = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "recorded_at": self.recorded_at.strftime("%Y-%m-%d %H:%M") if self.recorded_at else None,
            "blood_glucose": self.blood_glucose,
            "systolic_bp": self.systolic_bp,
            "diastolic_bp": self.diastolic_bp,
            "heart_rate": self.heart_rate,
            "oxygen_saturation": self.oxygen_saturation,
            "body_temperature": self.body_temperature,
            "weight_kg": self.weight_kg,
            "bmi": self.bmi,
            "sleep_hours": self.sleep_hours,
            "water_intake_liters": self.water_intake_liters,
            "exercise_minutes": self.exercise_minutes,
            "stress_level": self.stress_level,
            "pain_level": self.pain_level,
            "mood": self.mood,
            "symptoms": self.symptoms,
            "health_score": self.health_score,
            "risk_level": self.risk_level,
            "ai_summary": self.ai_summary,
        }

    def __repr__(self):
        return f"<HealthRecord patient={self.patient_id} @ {self.recorded_at}>"
