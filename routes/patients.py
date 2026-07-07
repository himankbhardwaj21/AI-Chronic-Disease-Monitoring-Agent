"""
routes/patients.py — Patient profile management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app_factory import db
from models.patient import Patient
from models.medication import Medication
from models.health_record import HealthRecord
from utils.validators import validate_patient_data
from utils.helpers import calculate_bmi
from config import AGENT_INSTRUCTIONS

patients_bp = Blueprint("patients", __name__)
DISEASES = AGENT_INSTRUCTIONS["supported_diseases"]


@patients_bp.route("/")
def list_patients():
    """List all patients."""
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.created_at.desc()).all()
    return render_template("patients/list.html", patients=patients, active_page="patients")


@patients_bp.route("/create", methods=["GET", "POST"])
def create():
    """Create new patient profile."""
    if request.method == "POST":
        data = request.form.to_dict()
        errors = validate_patient_data(data)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("patients/form.html", patient=None,
                                   diseases=DISEASES, active_page="patients")

        patient = Patient(
            name=data["name"],
            age=int(data["age"]),
            gender=data["gender"],
            dob=data.get("dob"),
            blood_group=data.get("blood_group"),
            height_cm=float(data["height_cm"]) if data.get("height_cm") else None,
            weight_kg=float(data["weight_kg"]) if data.get("weight_kg") else None,
            primary_disease=data["primary_disease"],
            secondary_diseases=data.get("secondary_diseases"),
            known_allergies=data.get("known_allergies"),
            medical_history=data.get("medical_history"),
            current_medications=data.get("current_medications"),
            doctor_name=data.get("doctor_name"),
            doctor_contact=data.get("doctor_contact"),
            next_appointment=data.get("next_appointment"),
            smoking_status=data.get("smoking_status"),
            alcohol_consumption=data.get("alcohol_consumption"),
            activity_level=data.get("activity_level"),
            emergency_contact_name=data.get("emergency_contact_name"),
            emergency_contact_phone=data.get("emergency_contact_phone"),
            emergency_contact_relation=data.get("emergency_contact_relation"),
        )
        db.session.add(patient)
        db.session.commit()
        flash(f"Patient profile created for {patient.name}!", "success")
        return redirect(url_for("dashboard.dashboard", patient_id=patient.id))

    return render_template("patients/form.html", patient=None,
                           diseases=DISEASES, active_page="patients")


@patients_bp.route("/<int:patient_id>")
def view(patient_id: int):
    """View patient profile."""
    patient = Patient.query.get_or_404(patient_id)
    medications = Medication.query.filter_by(patient_id=patient_id).order_by(
        Medication.is_active.desc(), Medication.name
    ).all()
    total_records = HealthRecord.query.filter_by(patient_id=patient_id).count()
    all_patients = Patient.query.filter_by(is_active=True).all()
    return render_template(
        "patients/view.html",
        patient=patient,
        medications=medications,
        total_records=total_records,
        all_patients=all_patients,
        active_page="patients",
    )


@patients_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
def edit(patient_id: int):
    """Edit patient profile."""
    patient = Patient.query.get_or_404(patient_id)
    if request.method == "POST":
        data = request.form.to_dict()
        errors = validate_patient_data(data)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("patients/form.html", patient=patient,
                                   diseases=DISEASES, active_page="patients")

        patient.name = data["name"]
        patient.age = int(data["age"])
        patient.gender = data["gender"]
        patient.dob = data.get("dob")
        patient.blood_group = data.get("blood_group")
        patient.height_cm = float(data["height_cm"]) if data.get("height_cm") else None
        patient.weight_kg = float(data["weight_kg"]) if data.get("weight_kg") else None
        patient.primary_disease = data["primary_disease"]
        patient.secondary_diseases = data.get("secondary_diseases")
        patient.known_allergies = data.get("known_allergies")
        patient.medical_history = data.get("medical_history")
        patient.current_medications = data.get("current_medications")
        patient.doctor_name = data.get("doctor_name")
        patient.doctor_contact = data.get("doctor_contact")
        patient.next_appointment = data.get("next_appointment")
        patient.smoking_status = data.get("smoking_status")
        patient.alcohol_consumption = data.get("alcohol_consumption")
        patient.activity_level = data.get("activity_level")
        patient.emergency_contact_name = data.get("emergency_contact_name")
        patient.emergency_contact_phone = data.get("emergency_contact_phone")
        patient.emergency_contact_relation = data.get("emergency_contact_relation")
        db.session.commit()
        flash("Patient profile updated successfully!", "success")
        return redirect(url_for("patients.view", patient_id=patient_id))

    return render_template("patients/form.html", patient=patient,
                           diseases=DISEASES, active_page="patients")


@patients_bp.route("/<int:patient_id>/delete", methods=["POST"])
def delete(patient_id: int):
    """Soft-delete a patient."""
    patient = Patient.query.get_or_404(patient_id)
    patient.is_active = False
    db.session.commit()
    flash(f"Patient {patient.name} removed.", "info")
    remaining = Patient.query.filter_by(is_active=True).first()
    if remaining:
        return redirect(url_for("dashboard.dashboard", patient_id=remaining.id))
    return redirect(url_for("patients.create"))


# --- Medication routes ---
@patients_bp.route("/<int:patient_id>/medications/add", methods=["POST"])
def add_medication(patient_id: int):
    """Add medication to patient."""
    data = request.form.to_dict()
    med = Medication(
        patient_id=patient_id,
        name=data.get("name", ""),
        dosage=data.get("dosage"),
        frequency=data.get("frequency"),
        timing=data.get("timing"),
        instructions=data.get("instructions"),
        purpose=data.get("purpose"),
        prescribing_doctor=data.get("prescribing_doctor"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        refill_date=data.get("refill_date"),
        is_active=True,
        total_doses=int(data.get("total_doses") or 0),
        taken_doses=int(data.get("taken_doses") or 0),
    )
    db.session.add(med)
    db.session.commit()
    flash(f"Medication '{med.name}' added successfully!", "success")
    return redirect(url_for("patients.view", patient_id=patient_id))


@patients_bp.route("/medications/<int:med_id>/taken", methods=["POST"])
def mark_medication_taken(med_id: int):
    """Mark a medication dose as taken."""
    from datetime import datetime
    med = Medication.query.get_or_404(med_id)
    med.taken_doses = (med.taken_doses or 0) + 1
    med.total_doses = max(med.total_doses or 0, med.taken_doses)
    med.last_taken = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "ok", "adherence": med.adherence_pct})


@patients_bp.route("/medications/<int:med_id>/delete", methods=["POST"])
def delete_medication(med_id: int):
    """Delete a medication."""
    med = Medication.query.get_or_404(med_id)
    patient_id = med.patient_id
    db.session.delete(med)
    db.session.commit()
    flash(f"Medication '{med.name}' removed.", "info")
    return redirect(url_for("patients.view", patient_id=patient_id))
