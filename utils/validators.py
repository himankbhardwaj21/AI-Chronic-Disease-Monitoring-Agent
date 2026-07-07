"""
utils/validators.py — Input validation for ChronicCare AI
"""


def validate_vitals(data: dict) -> list:
    """
    Validate health record input data.
    Returns list of error messages (empty if valid).
    """
    errors = []

    glucose = data.get("blood_glucose")
    if glucose is not None and glucose != "":
        try:
            g = float(glucose)
            if not (20 <= g <= 600):
                errors.append("Blood glucose must be between 20 and 600 mg/dL")
        except ValueError:
            errors.append("Blood glucose must be a number")

    systolic = data.get("systolic_bp")
    if systolic is not None and systolic != "":
        try:
            s = int(systolic)
            if not (60 <= s <= 300):
                errors.append("Systolic BP must be between 60 and 300 mmHg")
        except ValueError:
            errors.append("Systolic BP must be a whole number")

    diastolic = data.get("diastolic_bp")
    if diastolic is not None and diastolic != "":
        try:
            d = int(diastolic)
            if not (40 <= d <= 200):
                errors.append("Diastolic BP must be between 40 and 200 mmHg")
        except ValueError:
            errors.append("Diastolic BP must be a whole number")

    hr = data.get("heart_rate")
    if hr is not None and hr != "":
        try:
            h = int(hr)
            if not (20 <= h <= 250):
                errors.append("Heart rate must be between 20 and 250 bpm")
        except ValueError:
            errors.append("Heart rate must be a whole number")

    o2 = data.get("oxygen_saturation")
    if o2 is not None and o2 != "":
        try:
            o = float(o2)
            if not (50 <= o <= 100):
                errors.append("Oxygen saturation must be between 50 and 100%")
        except ValueError:
            errors.append("Oxygen saturation must be a number")

    temp = data.get("body_temperature")
    if temp is not None and temp != "":
        try:
            t = float(temp)
            if not (32 <= t <= 45):
                errors.append("Body temperature must be between 32 and 45°C")
        except ValueError:
            errors.append("Body temperature must be a number")

    sleep = data.get("sleep_hours")
    if sleep is not None and sleep != "":
        try:
            s = float(sleep)
            if not (0 <= s <= 24):
                errors.append("Sleep hours must be between 0 and 24")
        except ValueError:
            errors.append("Sleep hours must be a number")

    return errors


def validate_patient_data(data: dict) -> list:
    """
    Validate patient profile data.
    Returns list of error messages.
    """
    errors = []

    if not data.get("name") or len(data["name"].strip()) < 2:
        errors.append("Patient name must be at least 2 characters")

    age = data.get("age")
    if age is not None:
        try:
            a = int(age)
            if not (0 <= a <= 130):
                errors.append("Age must be between 0 and 130")
        except ValueError:
            errors.append("Age must be a whole number")

    if not data.get("gender"):
        errors.append("Gender is required")

    if not data.get("primary_disease"):
        errors.append("Primary disease is required")

    height = data.get("height_cm")
    if height:
        try:
            h = float(height)
            if not (50 <= h <= 300):
                errors.append("Height must be between 50 and 300 cm")
        except ValueError:
            errors.append("Height must be a number")

    weight = data.get("weight_kg")
    if weight:
        try:
            w = float(weight)
            if not (10 <= w <= 500):
                errors.append("Weight must be between 10 and 500 kg")
        except ValueError:
            errors.append("Weight must be a number")

    return errors
