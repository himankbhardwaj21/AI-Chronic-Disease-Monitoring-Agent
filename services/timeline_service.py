"""
services/timeline_service.py — Business logic for Feature 5: Health Timeline
Auto-generates timeline events from health records and user actions.
"""

from datetime import datetime, timedelta
from app_factory import db
from models.health_timeline import HealthTimeline
from models.health_record import HealthRecord


# Icon + color mappings for event types
EVENT_CONFIG = {
    "medication_taken":     ("bi-capsule-pill",           "success",  "medication"),
    "medication_missed":    ("bi-capsule",                 "danger",   "medication"),
    "blood_sugar_change":   ("bi-activity",                "warning",  "health"),
    "bp_change":            ("bi-droplet-fill",            "danger",   "health"),
    "doctor_visit":         ("bi-hospital",                "info",     "health"),
    "exercise":             ("bi-bicycle",                 "success",  "lifestyle"),
    "sleep_record":         ("bi-moon-stars-fill",         "primary",  "lifestyle"),
    "weight_change":        ("bi-graph-up",                "info",     "lifestyle"),
    "risk_change":          ("bi-shield-fill",             "warning",  "health"),
    "ai_recommendation":    ("bi-robot",                   "primary",  "ai"),
    "symptom":              ("bi-bandaid",                 "warning",  "health"),
    "mood":                 ("bi-emoji-smile",             "info",     "lifestyle"),
    "heart_rate":           ("bi-heart-pulse-fill",        "danger",   "health"),
    "oxygen":               ("bi-wind",                    "info",     "health"),
    "water_intake":         ("bi-droplet",                 "info",     "lifestyle"),
}


class TimelineService:

    @staticmethod
    def add_event(patient_id: int, event_type: str, title: str,
                  description: str = None, value: str = None,
                  previous_value: str = None, severity: str = "info",
                  health_record_id: int = None) -> HealthTimeline:
        """Add a single timeline event."""
        cfg = EVENT_CONFIG.get(event_type, ("bi-circle", "secondary", "health"))
        event = HealthTimeline(
            patient_id=patient_id,
            event_type=event_type,
            event_category=cfg[2],
            title=title,
            description=description,
            value=value,
            previous_value=previous_value,
            icon=cfg[0],
            color=cfg[1],
            severity=severity,
            health_record_id=health_record_id,
        )
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def generate_from_health_record(patient_id: int, record: HealthRecord,
                                    prev_record: HealthRecord = None):
        """Auto-generate timeline events when a health record is saved."""
        events_to_add = []
        rdict = record.to_dict()
        prev = prev_record.to_dict() if prev_record else {}

        # Blood sugar event
        if rdict.get("blood_glucose"):
            g = rdict["blood_glucose"]
            severity = "danger" if g >= 250 or g < 70 else ("warning" if g >= 180 else "success")
            prev_g = prev.get("blood_glucose")
            events_to_add.append(HealthTimeline(
                patient_id=patient_id,
                event_type="blood_sugar_change",
                event_category="health",
                title="Blood Sugar Recorded",
                description=f"Blood glucose reading: {g} mg/dL" + (
                    f" (was {prev_g} mg/dL)" if prev_g else ""
                ),
                value=f"{g} mg/dL",
                previous_value=f"{prev_g} mg/dL" if prev_g else None,
                icon="bi-activity",
                color="warning" if g >= 180 else "success",
                severity=severity,
                health_record_id=record.id,
                recorded_at=record.recorded_at,
            ))

        # Blood pressure event
        if rdict.get("systolic_bp"):
            s, d = rdict["systolic_bp"], rdict.get("diastolic_bp", "?")
            severity = "danger" if s >= 180 else ("warning" if s >= 140 else "success")
            events_to_add.append(HealthTimeline(
                patient_id=patient_id,
                event_type="bp_change",
                event_category="health",
                title="Blood Pressure Recorded",
                description=f"BP reading: {s}/{d} mmHg",
                value=f"{s}/{d} mmHg",
                icon="bi-droplet-fill",
                color="danger" if s >= 140 else "success",
                severity=severity,
                health_record_id=record.id,
                recorded_at=record.recorded_at,
            ))

        # Exercise event
        if rdict.get("exercise_minutes") and rdict["exercise_minutes"] > 0:
            ex = rdict["exercise_minutes"]
            events_to_add.append(HealthTimeline(
                patient_id=patient_id,
                event_type="exercise",
                event_category="lifestyle",
                title="Exercise Session",
                description=f"Completed {ex} minutes of physical activity",
                value=f"{ex} min",
                icon="bi-bicycle",
                color="success",
                severity="success",
                health_record_id=record.id,
                recorded_at=record.recorded_at,
            ))

        # Sleep event
        if rdict.get("sleep_hours"):
            sl = rdict["sleep_hours"]
            severity = "danger" if sl < 5 else ("warning" if sl < 6.5 else "success")
            events_to_add.append(HealthTimeline(
                patient_id=patient_id,
                event_type="sleep_record",
                event_category="lifestyle",
                title="Sleep Record",
                description=f"Slept {sl} hours",
                value=f"{sl} hrs",
                icon="bi-moon-stars-fill",
                color="primary",
                severity=severity,
                health_record_id=record.id,
                recorded_at=record.recorded_at,
            ))

        # Risk level change event
        if rdict.get("risk_level") and prev.get("risk_level"):
            if rdict["risk_level"] != prev["risk_level"]:
                events_to_add.append(HealthTimeline(
                    patient_id=patient_id,
                    event_type="risk_change",
                    event_category="health",
                    title=f"Risk Level Changed: {prev['risk_level']} → {rdict['risk_level']}",
                    description=f"Health risk level changed from {prev['risk_level']} to {rdict['risk_level']}",
                    value=rdict["risk_level"],
                    previous_value=prev["risk_level"],
                    icon="bi-shield-fill",
                    color="danger" if rdict["risk_level"] in ["High", "Critical"] else "warning",
                    severity="warning",
                    health_record_id=record.id,
                    recorded_at=record.recorded_at,
                ))

        # Mood event
        if rdict.get("mood"):
            events_to_add.append(HealthTimeline(
                patient_id=patient_id,
                event_type="mood",
                event_category="lifestyle",
                title=f"Mood: {rdict['mood']}",
                description=f"Reported mood: {rdict['mood']}" + (
                    f" | Stress: {rdict.get('stress_level', '?')}/10" if rdict.get("stress_level") else ""
                ),
                value=rdict["mood"],
                icon="bi-emoji-smile",
                color="info",
                severity="info",
                health_record_id=record.id,
                recorded_at=record.recorded_at,
            ))

        for ev in events_to_add:
            db.session.add(ev)
        db.session.commit()

    @staticmethod
    def get_timeline(patient_id: int, days: int = 7,
                     category: str = None) -> list:
        """Fetch timeline events for a patient, optionally filtered."""
        from datetime import datetime, timedelta
        since = datetime.utcnow() - timedelta(days=days)
        query = HealthTimeline.query.filter(
            HealthTimeline.patient_id == patient_id,
            HealthTimeline.recorded_at >= since,
        )
        if category and category != "all":
            query = query.filter(HealthTimeline.event_category == category)
        events = query.order_by(HealthTimeline.recorded_at.desc()).limit(200).all()
        return [e.to_dict() for e in events]

    @staticmethod
    def seed_from_existing_records(patient_id: int):
        """Backfill timeline events from existing health records (run once)."""
        existing_count = HealthTimeline.query.filter_by(patient_id=patient_id).count()
        if existing_count > 0:
            return  # Already seeded

        records = (
            HealthRecord.query.filter_by(patient_id=patient_id)
            .order_by(HealthRecord.recorded_at.asc())
            .all()
        )
        prev = None
        for rec in records:
            TimelineService.generate_from_health_record(patient_id, rec, prev)
            prev = rec
