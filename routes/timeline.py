"""
routes/timeline.py — Feature 5: AI Health Timeline
"""

from flask import Blueprint, render_template, jsonify, request
from models.patient import Patient
from services.timeline_service import TimelineService

timeline_bp = Blueprint("timeline", __name__)


@timeline_bp.route("/<int:patient_id>")
def timeline_page(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()

    # Backfill from existing records if needed
    TimelineService.seed_from_existing_records(patient_id)

    days = request.args.get("days", 7, type=int)
    category = request.args.get("category", "all")

    events = TimelineService.get_timeline(patient_id, days=days, category=category)

    # Group events by date for display
    grouped = {}
    for ev in events:
        date_key = ev["recorded_at"][:10] if ev["recorded_at"] else "Unknown"
        grouped.setdefault(date_key, []).append(ev)

    # Sort dates descending
    sorted_dates = sorted(grouped.keys(), reverse=True)

    return render_template(
        "features/timeline.html",
        patient=patient,
        all_patients=all_patients,
        grouped_events=[(d, grouped[d]) for d in sorted_dates],
        current_days=days,
        current_category=category,
        total_events=len(events),
        active_page="timeline",
    )


@timeline_bp.route("/api/<int:patient_id>/events")
def events_api(patient_id: int):
    days = request.args.get("days", 7, type=int)
    category = request.args.get("category", "all")
    events = TimelineService.get_timeline(patient_id, days=days, category=category)
    return jsonify({"events": events, "count": len(events)})
