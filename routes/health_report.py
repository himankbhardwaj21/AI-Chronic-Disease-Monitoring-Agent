"""
routes/health_report.py — Feature 1: AI Health Report Generator
"""

from flask import Blueprint, render_template, request, send_file, jsonify
from models.patient import Patient
from models.health_record import HealthRecord
from models.medication import Medication
from services.extended_agent_service import ExtendedAgentService
from services.report_service import ReportService
from services.health_service import HealthService
from utils.formatters import format_health_summary
import io

health_report_bp = Blueprint("health_report", __name__)


@health_report_bp.route("/<int:patient_id>")
def report_page(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    records = (
        HealthRecord.query.filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.asc())
        .limit(30).all()
    )
    medications = Medication.query.filter_by(patient_id=patient_id, is_active=True).all()
    records_dicts = [r.to_dict() for r in records]
    meds_dicts = [m.to_dict() for m in medications]

    result = ExtendedAgentService.generate_full_report(
        patient.to_dict(), records_dicts, meds_dicts
    )
    if result.get("report_content"):
        result["report_html"] = format_health_summary(result["report_content"])

    stats = HealthService.get_summary_stats(patient_id, days=30)
    from services.agent_service import AgentService
    risk = AgentService._calculate_risk_score(patient.to_dict(), records_dicts)

    return render_template(
        "features/health_report.html",
        patient=patient,
        all_patients=all_patients,
        result=result,
        stats=stats,
        risk=risk,
        active_page="health_report",
    )


@health_report_bp.route("/<int:patient_id>/pdf")
def download_pdf(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    records = (
        HealthRecord.query.filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.asc())
        .limit(30).all()
    )
    medications = Medication.query.filter_by(patient_id=patient_id, is_active=True).all()
    records_dicts = [r.to_dict() for r in records]
    meds_dicts = [m.to_dict() for m in medications]
    stats = HealthService.get_summary_stats(patient_id, days=30)

    result = ExtendedAgentService.generate_full_report(
        patient.to_dict(), records_dicts, meds_dicts
    )
    report_content = result.get("report_content", "No data available.")
    pdf_bytes = ReportService.generate_pdf(patient.to_dict(), report_content, stats, "full")

    from datetime import datetime
    filename = (
        f"HealthReport_{patient.name.replace(' ','_')}"
        f"_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    )
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@health_report_bp.route("/api/<int:patient_id>/regenerate", methods=["POST"])
def regenerate(patient_id: int):
    """AJAX: regenerate report on demand."""
    patient = Patient.query.get_or_404(patient_id)
    records = (
        HealthRecord.query.filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.asc())
        .limit(30).all()
    )
    medications = Medication.query.filter_by(patient_id=patient_id, is_active=True).all()
    result = ExtendedAgentService.generate_full_report(
        patient.to_dict(), [r.to_dict() for r in records], [m.to_dict() for m in medications]
    )
    if result.get("report_content"):
        result["report_html"] = format_health_summary(result["report_content"])
    return jsonify(result)
