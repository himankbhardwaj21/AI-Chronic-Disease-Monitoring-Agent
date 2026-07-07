"""
app_factory.py — Flask application factory and shared extensions
Separate from app.py to avoid circular imports.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_map, APP_META
import os

# Shared SQLAlchemy instance
db = SQLAlchemy()


def create_app(env: str = None) -> Flask:
    """Create and configure the Flask application."""
    env = env or os.getenv("FLASK_ENV", "development")
    cfg = config_map.get(env, config_map["default"])

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(cfg)
    app.config["APP_META"] = APP_META

    # Ensure data directory exists for SQLite (use absolute path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # Override DB URI with absolute path if using relative sqlite
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///") and not db_uri.startswith("sqlite:////"):
        db_name = db_uri.replace("sqlite:///", "")
        if not os.path.isabs(db_name):
            abs_path = os.path.join(data_dir, os.path.basename(db_name))
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{abs_path}"

    # Initialize extensions
    db.init_app(app)

    # Register blueprints — original
    from routes.dashboard import dashboard_bp
    from routes.patients import patients_bp
    from routes.health_data import health_data_bp
    from routes.agents import agents_bp
    from routes.chat import chat_bp
    from routes.reports import reports_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp, url_prefix="/patients")
    app.register_blueprint(health_data_bp, url_prefix="/health")
    app.register_blueprint(agents_bp, url_prefix="/agents")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    # Register blueprints — extended features
    from routes.health_report import health_report_bp
    from routes.prediction import prediction_bp
    from routes.emergency import emergency_bp
    from routes.timeline import timeline_bp
    from routes.goals import goals_bp
    from routes.explain import explain_bp

    app.register_blueprint(health_report_bp, url_prefix="/health-report")
    app.register_blueprint(prediction_bp, url_prefix="/prediction")
    app.register_blueprint(emergency_bp, url_prefix="/emergency")
    app.register_blueprint(timeline_bp, url_prefix="/timeline")
    app.register_blueprint(goals_bp, url_prefix="/goals")
    app.register_blueprint(explain_bp, url_prefix="/explain")

    # Create all database tables
    with app.app_context():
        db.create_all()
        _seed_demo_data(app)

    return app


def _seed_demo_data(app: Flask):
    """Seed a demo patient if the database is empty."""
    from models.patient import Patient
    from models.medication import Medication
    from models.health_record import HealthRecord
    from datetime import datetime, timedelta
    import random

    if Patient.query.count() > 0:
        return  # Already seeded

    # Demo patient
    patient = Patient(
        name="Rajesh Kumar",
        age=54,
        gender="Male",
        dob="1970-03-15",
        blood_group="B+",
        height_cm=172.0,
        weight_kg=82.5,
        primary_disease="Type 2 Diabetes",
        secondary_diseases="Hypertension",
        known_allergies="Penicillin",
        medical_history="Diagnosed with T2DM in 2015, Hypertension in 2018",
        current_medications="Metformin 500mg, Amlodipine 5mg, Aspirin 75mg",
        doctor_name="Dr. Priya Sharma",
        doctor_contact="+91-98765-43210",
        next_appointment="2025-08-15",
        smoking_status="Former",
        alcohol_consumption="Occasional",
        activity_level="Light",
        emergency_contact_name="Sunita Kumar",
        emergency_contact_phone="+91-98765-11111",
        emergency_contact_relation="Spouse",
    )
    db.session.add(patient)
    db.session.flush()

    # Demo medications
    meds = [
        Medication(
            patient_id=patient.id,
            name="Metformin",
            dosage="500mg",
            frequency="Twice daily",
            timing="Morning 8am, Night 8pm",
            purpose="Blood sugar control",
            prescribing_doctor="Dr. Priya Sharma",
            start_date="2015-06-01",
            is_active=True,
            total_doses=60,
            taken_doses=54,
        ),
        Medication(
            patient_id=patient.id,
            name="Amlodipine",
            dosage="5mg",
            frequency="Once daily",
            timing="Morning 8am",
            purpose="Blood pressure control",
            prescribing_doctor="Dr. Priya Sharma",
            start_date="2018-03-10",
            is_active=True,
            total_doses=30,
            taken_doses=29,
        ),
        Medication(
            patient_id=patient.id,
            name="Aspirin",
            dosage="75mg",
            frequency="Once daily",
            timing="Morning with breakfast",
            purpose="Cardiovascular protection",
            prescribing_doctor="Dr. Priya Sharma",
            start_date="2020-01-15",
            is_active=True,
            total_doses=30,
            taken_doses=28,
        ),
    ]
    db.session.add_all(meds)

    # Demo health records (last 14 days)
    base_glucose = 145
    base_systolic = 138
    base_diastolic = 88
    base_hr = 78
    for i in range(14):
        day = datetime.utcnow() - timedelta(days=13 - i)
        rec = HealthRecord(
            patient_id=patient.id,
            recorded_at=day,
            blood_glucose=round(base_glucose + random.uniform(-15, 20), 1),
            systolic_bp=base_systolic + random.randint(-8, 10),
            diastolic_bp=base_diastolic + random.randint(-5, 8),
            heart_rate=base_hr + random.randint(-8, 10),
            oxygen_saturation=round(97.5 + random.uniform(-2, 1), 1),
            body_temperature=round(36.6 + random.uniform(-0.3, 0.5), 1),
            weight_kg=round(82.5 + random.uniform(-0.5, 0.5), 1),
            bmi=round(27.9 + random.uniform(-0.2, 0.2), 1),
            sleep_hours=round(6.5 + random.uniform(-1, 1.5), 1),
            water_intake_liters=round(1.8 + random.uniform(-0.3, 0.5), 1),
            exercise_minutes=random.randint(15, 45),
            calories_burned=random.randint(180, 320),
            steps_count=random.randint(4000, 8500),
            stress_level=random.randint(4, 8),
            pain_level=random.randint(1, 4),
            mood=random.choice(["Good", "Fair", "Good", "Fair", "Poor"]),
            symptoms="Mild fatigue, Occasional headache",
            health_score=round(65 + random.uniform(-10, 15), 1),
            risk_level=random.choice(["Medium", "Medium", "High", "Medium"]),
        )
        db.session.add(rec)

    db.session.commit()
