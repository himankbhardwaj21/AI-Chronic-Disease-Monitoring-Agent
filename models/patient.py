"""
models/patient.py — Patient SQLAlchemy model
Stores complete patient profile for chronic disease monitoring.
"""

from datetime import datetime
from app_factory import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(20))
    blood_group = db.Column(db.String(10))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)

    # Disease & Medical Info
    primary_disease = db.Column(db.String(100), nullable=False)
    secondary_diseases = db.Column(db.Text)          # comma-separated
    known_allergies = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    doctor_name = db.Column(db.String(120))
    doctor_contact = db.Column(db.String(50))
    next_appointment = db.Column(db.String(50))

    # Lifestyle
    smoking_status = db.Column(db.String(30))        # Never / Former / Current
    alcohol_consumption = db.Column(db.String(30))   # None / Occasional / Frequent
    activity_level = db.Column(db.String(30))        # Sedentary / Light / Moderate / Active

    # Emergency Contact
    emergency_contact_name = db.Column(db.String(120))
    emergency_contact_phone = db.Column(db.String(30))
    emergency_contact_relation = db.Column(db.String(50))

    # Profile metadata
    profile_photo = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    health_records = db.relationship("HealthRecord", backref="patient", lazy=True, cascade="all, delete-orphan")
    medications = db.relationship("Medication", backref="patient", lazy=True, cascade="all, delete-orphan")
    alerts = db.relationship("Alert", backref="patient", lazy=True, cascade="all, delete-orphan")

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg:
            h = self.height_cm / 100
            return round(self.weight_kg / (h * h), 1)
        return None

    @property
    def latest_record(self):
        from models.health_record import HealthRecord as HR
        return (
            HR.query.filter_by(patient_id=self.id)
            .order_by(HR.recorded_at.desc())
            .first()
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "bmi": self.bmi,
            "primary_disease": self.primary_disease,
            "secondary_diseases": self.secondary_diseases,
            "known_allergies": self.known_allergies,
            "doctor_name": self.doctor_name,
            "doctor_contact": self.doctor_contact,
            "next_appointment": self.next_appointment,
            "smoking_status": self.smoking_status,
            "alcohol_consumption": self.alcohol_consumption,
            "activity_level": self.activity_level,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "created_at": str(self.created_at),
        }

    def __repr__(self):
        return f"<Patient {self.name} | {self.primary_disease}>"
