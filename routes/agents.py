"""
routes/agents.py — AI Agent endpoints (all 5 agents)
"""

from flask import Blueprint, render_template, request, jsonify
from models.patient import Patient
from models.health_record import HealthRecord
from models.medication import Medication
from services.agent_service import AgentService
from utils.formatters import format_health_summary, format_medication_schedule

agents_bp = Blueprint("agents", __name__)


def _get_patient_context(patient_id: int):
    """Helper to fetch patient, records, medications."""
    patient = Patient.query.get_or_404(patient_id)
    records = (
        HealthRecord.query
        .filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.asc())
        .limit(30)
        .all()
    )
    medications = Medication.query.filter_by(patient_id=patient_id, is_active=True).all()
    return patient, records, medications


@agents_bp.route("/<int:patient_id>")
def agents_home(patient_id: int):
    """AI Agents landing page."""
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    return render_template(
        "agents/agents_home.html",
        patient=patient,
        all_patients=all_patients,
        active_page="agents",
    )


@agents_bp.route("/<int:patient_id>/vitals", methods=["GET", "POST"])
def vitals_analysis(patient_id: int):
    """Agent 1: Health Monitoring — analyze vitals."""
    patient, records, medications = _get_patient_context(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    result = None

    if request.method == "POST" or records:
        latest = records[-1] if records else None
        if latest:
            result = AgentService.analyze_vitals(
                patient.to_dict(), latest.to_dict()
            )
            if result.get("analysis"):
                result["analysis_html"] = format_health_summary(result["analysis"])

    return render_template(
        "agents/vitals_analysis.html",
        patient=patient,
        all_patients=all_patients,
        result=result,
        latest_record=records[-1] if records else None,
        active_page="agents",
    )


@agents_bp.route("/<int:patient_id>/risk", methods=["GET", "POST"])
def risk_prediction(patient_id: int):
    """Agent 2: Risk Prediction."""
    patient, records, medications = _get_patient_context(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    result = None

    if records:
        records_dicts = [r.to_dict() for r in records]
        result = AgentService.predict_risk(patient.to_dict(), records_dicts)
        if result.get("analysis"):
            result["analysis_html"] = format_health_summary(result["analysis"])

    return render_template(
        "agents/risk_prediction.html",
        patient=patient,
        all_patients=all_patients,
        result=result,
        active_page="agents",
    )


@agents_bp.route("/<int:patient_id>/medication", methods=["GET", "POST"])
def medication_guidance(patient_id: int):
    """Agent 3: Medication Assistant."""
    patient, records, medications = _get_patient_context(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    meds_dicts = [m.to_dict() for m in medications]
    result = AgentService.medication_guidance(patient.to_dict(), meds_dicts)

    if result.get("analysis"):
        result["analysis_html"] = format_health_summary(result["analysis"])

    schedule = format_medication_schedule(meds_dicts)

    return render_template(
        "agents/medication_guidance.html",
        patient=patient,
        all_patients=all_patients,
        result=result,
        schedule=schedule,
        medications=medications,
        active_page="agents",
    )


@agents_bp.route("/<int:patient_id>/lifestyle", methods=["GET", "POST"])
def lifestyle_recommendations(patient_id: int):
    """Agent 4: Lifestyle Recommendations."""
    patient, records, medications = _get_patient_context(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    latest_record = records[-1].to_dict() if records else {}
    result = AgentService.lifestyle_recommendations(patient.to_dict(), latest_record)

    if result.get("recommendations"):
        result["recommendations_html"] = format_health_summary(result["recommendations"])

    return render_template(
        "agents/lifestyle_recommendations.html",
        patient=patient,
        all_patients=all_patients,
        result=result,
        latest_record=records[-1] if records else None,
        active_page="agents",
    )


@agents_bp.route("/<int:patient_id>/report", methods=["GET", "POST"])
def report_agent(patient_id: int):
    """Agent 5: Medical Report Generator."""
    patient, records, medications = _get_patient_context(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    report_type = request.args.get("type", "weekly")
    records_dicts = [r.to_dict() for r in records]
    meds_dicts = [m.to_dict() for m in medications]

    result = AgentService.generate_report(
        patient.to_dict(), records_dicts, meds_dicts, report_type
    )
    if result.get("report_content"):
        result["report_html"] = format_health_summary(result["report_content"])

    return render_template(
        "agents/report_agent.html",
        patient=patient,
        all_patients=all_patients,
        result=result,
        report_type=report_type,
        active_page="agents",
    )


# AJAX endpoints for quick AI analysis
@agents_bp.route("/api/<int:patient_id>/quick-analysis", methods=["POST"])
def quick_analysis(patient_id: int):
    """AJAX: run quick AI analysis on demand."""
    agent_type = request.json.get("agent", "vitals")
    patient, records, medications = _get_patient_context(patient_id)

    try:
        if agent_type == "vitals" and records:
            result = AgentService.analyze_vitals(patient.to_dict(), records[-1].to_dict())
        elif agent_type == "risk" and records:
            result = AgentService.predict_risk(patient.to_dict(), [r.to_dict() for r in records])
        elif agent_type == "lifestyle" and records:
            result = AgentService.lifestyle_recommendations(patient.to_dict(), records[-1].to_dict())
        else:
            return jsonify({"error": "No data available"}), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
