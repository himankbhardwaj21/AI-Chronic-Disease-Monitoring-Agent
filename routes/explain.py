"""
routes/explain.py — Feature 3: Explainable AI endpoint
"""

from flask import Blueprint, request, jsonify
from models.patient import Patient
from models.health_record import HealthRecord
from services.extended_agent_service import ExtendedAgentService
from utils.formatters import format_health_summary

explain_bp = Blueprint("explain", __name__)


@explain_bp.route("/api/<int:patient_id>/why", methods=["POST"])
def explain_why(patient_id: int):
    """
    AJAX endpoint: explain any AI recommendation.
    Body: { "recommendation": "...", "context_type": "risk|vitals|lifestyle|medication" }
    """
    patient = Patient.query.get_or_404(patient_id)
    data = request.json or {}
    recommendation = data.get("recommendation", "").strip()
    context_type = data.get("context_type", "general")

    if not recommendation:
        return jsonify({"error": "No recommendation text provided"}), 400

    records = (
        HealthRecord.query.filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.desc())
        .limit(10).all()
    )
    records_dicts = [r.to_dict() for r in reversed(records)]

    explanation = ExtendedAgentService.explain_recommendation(
        patient.to_dict(), recommendation, records_dicts, context_type
    )
    return jsonify({
        "explanation": explanation,
        "explanation_html": format_health_summary(explanation),
        "status": "success",
    })
