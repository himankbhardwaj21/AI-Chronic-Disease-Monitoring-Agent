"""
utils/helpers.py — Common utility functions for ChronicCare AI
"""

from datetime import datetime, date


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight (kg) and height (cm)."""
    if not weight_kg or not height_cm:
        return None
    h = height_cm / 100
    return round(weight_kg / (h * h), 1)


def calculate_age(dob_str: str) -> int:
    """Calculate age from date of birth string (YYYY-MM-DD)."""
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except Exception:
        return 0


def format_date(dt) -> str:
    """Format datetime to readable string."""
    if isinstance(dt, datetime):
        return dt.strftime("%B %d, %Y")
    if isinstance(dt, str):
        try:
            return datetime.strptime(dt, "%Y-%m-%d").strftime("%B %d, %Y")
        except Exception:
            return dt
    return str(dt) if dt else "N/A"


def get_risk_color(risk_level: str) -> str:
    """Return Bootstrap color class for risk level."""
    mapping = {
        "Low": "success",
        "Medium": "warning",
        "High": "danger",
        "Critical": "danger",
        "Emergency": "danger",
        "Unknown": "secondary",
    }
    return mapping.get(risk_level, "secondary")


def get_severity_icon(severity: str) -> str:
    """Return Bootstrap icon for alert severity."""
    mapping = {
        "Info": "bi-info-circle-fill text-info",
        "Warning": "bi-exclamation-triangle-fill text-warning",
        "Critical": "bi-x-octagon-fill text-danger",
        "Emergency": "bi-heart-pulse-fill text-danger",
    }
    return mapping.get(severity, "bi-bell-fill text-secondary")


def get_bp_category(systolic: int, diastolic: int) -> str:
    """Classify blood pressure reading."""
    if not systolic:
        return "Unknown"
    if systolic < 120 and diastolic < 80:
        return "Normal"
    if systolic < 130 and diastolic < 80:
        return "Elevated"
    if systolic < 140 or diastolic < 90:
        return "Stage 1 High"
    if systolic >= 180 or diastolic >= 120:
        return "Hypertensive Crisis"
    return "Stage 2 High"


def get_glucose_category(glucose: float, fasting: bool = True) -> str:
    """Classify blood glucose reading."""
    if not glucose:
        return "Unknown"
    if fasting:
        if glucose < 70:
            return "Low (Hypoglycemia)"
        if glucose < 100:
            return "Normal"
        if glucose < 126:
            return "Prediabetes"
        return "Diabetes Range"
    # Post-meal
    if glucose < 140:
        return "Normal"
    if glucose < 200:
        return "Impaired"
    return "Diabetes Range"


def calculate_streak(records: list) -> int:
    """Calculate consecutive days with health records."""
    if not records:
        return 0
    streak = 0
    today = date.today()
    check_date = today
    record_dates = {r.recorded_at.date() for r in records if r.recorded_at}
    while check_date in record_dates:
        streak += 1
        check_date = date(check_date.year, check_date.month, check_date.day - 1)
        if check_date.day == 0:
            break
    return streak


def get_bmi_category(bmi: float) -> str:
    """Classify BMI value."""
    if not bmi:
        return "Unknown"
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    if bmi < 35:
        return "Obese Class I"
    return "Obese Class II+"
