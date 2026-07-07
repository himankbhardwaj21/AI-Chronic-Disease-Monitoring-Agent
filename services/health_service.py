"""
services/health_service.py — Business logic for health data management
"""

from app_factory import db
from models.health_record import HealthRecord
from models.alert import Alert
from models.patient import Patient
from services.agent_service import AgentService
from datetime import datetime, timedelta


class HealthService:
    """Service layer for health record CRUD and analytics."""

    @staticmethod
    def save_health_record(patient_id: int, form_data: dict) -> dict:
        """Save a new health record and run AI analysis."""
        patient = Patient.query.get_or_404(patient_id)

        # Calculate BMI if weight provided
        weight = form_data.get("weight_kg")
        bmi = None
        if weight and patient.height_cm:
            h = patient.height_cm / 100
            bmi = round(float(weight) / (h * h), 1)

        record = HealthRecord(
            patient_id=patient_id,
            blood_glucose=form_data.get("blood_glucose") or None,
            systolic_bp=form_data.get("systolic_bp") or None,
            diastolic_bp=form_data.get("diastolic_bp") or None,
            heart_rate=form_data.get("heart_rate") or None,
            oxygen_saturation=form_data.get("oxygen_saturation") or None,
            body_temperature=form_data.get("body_temperature") or None,
            pulse=form_data.get("pulse") or None,
            weight_kg=weight or None,
            bmi=bmi,
            sleep_hours=form_data.get("sleep_hours") or None,
            water_intake_liters=form_data.get("water_intake_liters") or None,
            exercise_minutes=form_data.get("exercise_minutes") or None,
            calories_burned=form_data.get("calories_burned") or None,
            steps_count=form_data.get("steps_count") or None,
            stress_level=form_data.get("stress_level") or None,
            pain_level=form_data.get("pain_level") or None,
            mood=form_data.get("mood"),
            symptoms=form_data.get("symptoms"),
            notes=form_data.get("notes"),
        )

        # Calculate health score — use explicit dict to avoid SQLAlchemy internals
        record_dict = {
            "systolic_bp": record.systolic_bp,
            "diastolic_bp": record.diastolic_bp,
            "blood_glucose": record.blood_glucose,
            "heart_rate": record.heart_rate,
            "oxygen_saturation": record.oxygen_saturation,
            "body_temperature": record.body_temperature,
            "sleep_hours": record.sleep_hours,
            "exercise_minutes": record.exercise_minutes,
            "stress_level": record.stress_level,
        }
        record.health_score = AgentService._calculate_health_score(record_dict)

        # Determine risk level from score
        if record.health_score >= 80:
            record.risk_level = "Low"
        elif record.health_score >= 60:
            record.risk_level = "Medium"
        elif record.health_score >= 40:
            record.risk_level = "High"
        else:
            record.risk_level = "Critical"

        db.session.add(record)

        # Generate and save alerts
        from config import AGENT_INSTRUCTIONS
        thresholds = AGENT_INSTRUCTIONS["alert_thresholds"]
        alerts = AgentService._detect_vital_alerts(patient.to_dict(), record_dict, thresholds)
        for a in alerts:
            alert = Alert(
                patient_id=patient_id,
                alert_type="vital",
                severity=a["severity"],
                title=a["title"],
                message=a["message"],
                recommended_action=a["action"],
                triggered_by=a["triggered_by"],
                triggered_value=str(record_dict.get(a["triggered_by"], "")),
            )
            db.session.add(alert)

        db.session.commit()
        return {"record_id": record.id, "health_score": record.health_score, "risk_level": record.risk_level}

    @staticmethod
    def get_chart_data(patient_id: int, days: int = 14) -> dict:
        """Return chart-ready data for the last N days."""
        since = datetime.utcnow() - timedelta(days=days)
        records = (
            HealthRecord.query
            .filter_by(patient_id=patient_id)
            .filter(HealthRecord.recorded_at >= since)
            .order_by(HealthRecord.recorded_at.asc())
            .all()
        )

        labels = []
        glucose = []
        systolic = []
        diastolic = []
        heart_rate = []
        oxygen = []
        temperature = []
        health_scores = []
        sleep = []
        exercise = []
        stress = []
        weight = []

        for r in records:
            labels.append(r.recorded_at.strftime("%m/%d"))
            glucose.append(r.blood_glucose)
            systolic.append(r.systolic_bp)
            diastolic.append(r.diastolic_bp)
            heart_rate.append(r.heart_rate)
            oxygen.append(r.oxygen_saturation)
            temperature.append(r.body_temperature)
            health_scores.append(r.health_score)
            sleep.append(r.sleep_hours)
            exercise.append(r.exercise_minutes)
            stress.append(r.stress_level)
            weight.append(r.weight_kg)

        return {
            "labels": labels,
            "blood_glucose": glucose,
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "heart_rate": heart_rate,
            "oxygen_saturation": oxygen,
            "body_temperature": temperature,
            "health_scores": health_scores,
            "sleep_hours": sleep,
            "exercise_minutes": exercise,
            "stress_levels": stress,
            "weight": weight,
        }

    @staticmethod
    def get_summary_stats(patient_id: int, days: int = 7) -> dict:
        """Return average stats for summary cards."""
        since = datetime.utcnow() - timedelta(days=days)
        records = (
            HealthRecord.query
            .filter_by(patient_id=patient_id)
            .filter(HealthRecord.recorded_at >= since)
            .all()
        )
        if not records:
            return {}

        def avg(field):
            vals = [getattr(r, field) for r in records if getattr(r, field) is not None]
            return round(sum(vals) / len(vals), 1) if vals else None

        return {
            "count": len(records),
            "avg_glucose": avg("blood_glucose"),
            "avg_systolic": avg("systolic_bp"),
            "avg_diastolic": avg("diastolic_bp"),
            "avg_hr": avg("heart_rate"),
            "avg_o2": avg("oxygen_saturation"),
            "avg_temp": avg("body_temperature"),
            "avg_sleep": avg("sleep_hours"),
            "avg_exercise": avg("exercise_minutes"),
            "avg_stress": avg("stress_level"),
            "avg_health_score": avg("health_score"),
        }
