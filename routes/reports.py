"""
routes/reports.py — Report generation and PDF download
"""

from flask import Blueprint, render_template, request, send_file, jsonify, flash, redirect, url_for
from models.patient import Patient
from models.health_record import HealthRecord
from models.medication import Medication
from services.agent_service import AgentService
from services.health_service import HealthService
from services.report_service import ReportService
from utils.formatters import format_health_summary
import io

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/<int:patient_id>")
def reports_home(patient_id: int):
    """Reports landing page."""
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    report_type = request.args.get("type", "weekly")

    records = (
        HealthRecord.query
        .filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.asc())
        .limit(60)
        .all()
    )
    medications = Medication.query.filter_by(patient_id=patient_id, is_active=True).all()
    records_dicts = [r.to_dict() for r in records]
    meds_dicts = [m.to_dict() for m in medications]

    result = AgentService.generate_report(
        patient.to_dict(), records_dicts, meds_dicts, report_type
    )
    if result.get("report_content"):
        result["report_html"] = format_health_summary(result["report_content"])

    # Stats for the period
    day_map = {"daily": 1, "weekly": 7, "monthly": 30}
    stats = HealthService.get_summary_stats(patient_id, days=day_map.get(report_type, 7))
    chart_data_obj = HealthService.get_chart_data(patient_id, days=day_map.get(report_type, 7))

    import json
    return render_template(
        "reports/reports.html",
        patient=patient,
        all_patients=all_patients,
        result=result,
        report_type=report_type,
        stats=stats,
        chart_data=json.dumps(chart_data_obj),
        active_page="reports",
    )


@reports_bp.route("/<int:patient_id>/pdf")
def download_pdf(patient_id: int):
    """Download PDF health report."""
    report_type = request.args.get("type", "weekly")
    patient = Patient.query.get_or_404(patient_id)

    records = (
        HealthRecord.query
        .filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.asc())
        .limit(60)
        .all()
    )
    medications = Medication.query.filter_by(patient_id=patient_id, is_active=True).all()
    records_dicts = [r.to_dict() for r in records]
    meds_dicts = [m.to_dict() for m in medications]

    day_map = {"daily": 1, "weekly": 7, "monthly": 30}
    stats = HealthService.get_summary_stats(patient_id, days=day_map.get(report_type, 7))

    # Generate AI report
    ai_result = AgentService.generate_report(
        patient.to_dict(), records_dicts, meds_dicts, report_type
    )
    report_content = ai_result.get("report_content", "No AI analysis available.")

    # Generate PDF
    pdf_bytes = ReportService.generate_pdf(
        patient.to_dict(), report_content, stats, report_type
    )

    from datetime import datetime
    filename = f"ChronicCare_{patient.name.replace(' ', '_')}_{report_type}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
