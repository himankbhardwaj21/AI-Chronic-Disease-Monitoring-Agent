"""
routes/goals.py — Feature 6: Smart Health Goals
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app_factory import db
from models.patient import Patient
from models.health_goal import HealthGoal
from models.health_record import HealthRecord
from services.extended_agent_service import ExtendedAgentService
from datetime import datetime, timedelta

goals_bp = Blueprint("goals", __name__)

GOAL_PRESETS = {
    "reduce_blood_sugar": {
        "title": "Reduce Blood Sugar",
        "icon": "bi-activity",
        "color": "warning",
        "unit": "mg/dL",
        "description": "Lower fasting blood glucose to target range",
    },
    "reduce_bp": {
        "title": "Reduce Blood Pressure",
        "icon": "bi-droplet-fill",
        "color": "danger",
        "unit": "mmHg",
        "description": "Bring systolic blood pressure to healthy range",
    },
    "lose_weight": {
        "title": "Lose Weight",
        "icon": "bi-graph-down",
        "color": "success",
        "unit": "kg",
        "description": "Achieve healthy body weight",
    },
    "improve_sleep": {
        "title": "Improve Sleep",
        "icon": "bi-moon-stars-fill",
        "color": "primary",
        "unit": "hrs/night",
        "description": "Get 7-9 hours of quality sleep",
    },
    "drink_water": {
        "title": "Drink More Water",
        "icon": "bi-droplet",
        "color": "info",
        "unit": "L/day",
        "description": "Reach daily hydration goal of 2.5L",
    },
    "exercise_daily": {
        "title": "Exercise Daily",
        "icon": "bi-bicycle",
        "color": "success",
        "unit": "min/day",
        "description": "Complete daily physical activity goal",
    },
    "improve_heart_health": {
        "title": "Improve Heart Health",
        "icon": "bi-heart-pulse-fill",
        "color": "danger",
        "unit": "bpm",
        "description": "Bring resting heart rate to healthy range",
    },
    "custom": {
        "title": "Custom Goal",
        "icon": "bi-trophy",
        "color": "primary",
        "unit": "",
        "description": "Set your own health goal",
    },
}

BADGE_ICONS = {
    "Sugar Champion":    "bi-trophy-fill text-warning",
    "BP Warrior":        "bi-shield-fill text-danger",
    "Weight Hero":       "bi-star-fill text-success",
    "Sleep Master":      "bi-moon-stars-fill text-primary",
    "Hydration Star":    "bi-droplet-fill text-info",
    "Fitness Champion":  "bi-bicycle text-success",
    "Heart Guardian":    "bi-heart-pulse-fill text-danger",
    "Goal Achiever":     "bi-award-fill text-warning",
    "Almost There":      "bi-flag-fill text-info",
    "Halfway Hero":      "bi-check2-circle text-success",
    "Good Start":        "bi-play-circle-fill text-primary",
}


@goals_bp.route("/<int:patient_id>")
def goals_page(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    goals = (
        HealthGoal.query.filter_by(patient_id=patient_id)
        .order_by(HealthGoal.created_at.desc())
        .all()
    )
    # Recalculate progress for each goal
    _refresh_goal_progress(patient_id, goals)

    return render_template(
        "features/goals.html",
        patient=patient,
        all_patients=all_patients,
        goals=goals,
        goal_presets=GOAL_PRESETS,
        badge_icons=BADGE_ICONS,
        active_page="goals",
    )


@goals_bp.route("/<int:patient_id>/create", methods=["POST"])
def create_goal(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    data = request.form.to_dict()
    goal_type = data.get("goal_type", "custom")
    preset = GOAL_PRESETS.get(goal_type, GOAL_PRESETS["custom"])

    # Parse dates
    target_date = None
    if data.get("target_date"):
        try:
            target_date = datetime.strptime(data["target_date"], "%Y-%m-%d")
        except ValueError:
            target_date = datetime.utcnow() + timedelta(days=30)

    baseline = float(data["baseline_value"]) if data.get("baseline_value") else None
    target = float(data["target_value"]) if data.get("target_value") else None

    goal = HealthGoal(
        patient_id=patient_id,
        goal_type=goal_type,
        title=data.get("title") or preset["title"],
        description=data.get("description") or preset["description"],
        icon=preset["icon"],
        color=preset["color"],
        target_value=target,
        target_unit=data.get("target_unit") or preset["unit"],
        baseline_value=baseline,
        current_value=baseline,
        start_date=datetime.utcnow(),
        target_date=target_date,
        status="active",
    )
    db.session.add(goal)
    db.session.commit()

    # Generate initial AI coaching
    _refresh_coaching(patient, goal)

    flash(f"Goal '{goal.title}' created! AI coaching has been generated.", "success")
    return redirect(url_for("goals.goals_page", patient_id=patient_id))


@goals_bp.route("/<int:patient_id>/update/<int:goal_id>", methods=["POST"])
def update_progress(patient_id: int, goal_id: int):
    """Update current value for a goal."""
    goal = HealthGoal.query.get_or_404(goal_id)
    data = request.form.to_dict()
    new_value = float(data.get("current_value", goal.current_value or 0))
    goal.current_value = new_value
    goal.progress_pct = goal.calc_progress()

    # Check completion
    if goal.progress_pct >= 100 and goal.status == "active":
        goal.status = "completed"
        goal.completed_at = datetime.utcnow()
        badge = ExtendedAgentService.check_goal_badge(goal.goal_type, goal.progress_pct)
        if badge:
            goal.badge_earned = badge
            goal.badge_earned_at = datetime.utcnow()
        flash(f"Congratulations! You've achieved your goal: {goal.title}!", "success")

    db.session.commit()
    flash(f"Progress updated to {new_value} {goal.target_unit or ''}!", "success")
    return redirect(url_for("goals.goals_page", patient_id=patient_id))


@goals_bp.route("/<int:patient_id>/delete/<int:goal_id>", methods=["POST"])
def delete_goal(patient_id: int, goal_id: int):
    goal = HealthGoal.query.get_or_404(goal_id)
    db.session.delete(goal)
    db.session.commit()
    flash("Goal removed.", "info")
    return redirect(url_for("goals.goals_page", patient_id=patient_id))


@goals_bp.route("/api/<int:patient_id>/coach/<int:goal_id>", methods=["POST"])
def get_coaching(patient_id: int, goal_id: int):
    """AJAX: regenerate AI coaching for a goal."""
    patient = Patient.query.get_or_404(patient_id)
    goal = HealthGoal.query.get_or_404(goal_id)
    _refresh_coaching(patient, goal)
    return jsonify({
        "coaching_tip": goal.ai_coaching_tip,
        "motivational_message": goal.motivational_message,
        "status": "ok",
    })


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def _refresh_goal_progress(patient_id: int, goals: list):
    """Update current_value from latest health record for auto-trackable goals."""
    latest = (
        HealthRecord.query.filter_by(patient_id=patient_id)
        .order_by(HealthRecord.recorded_at.desc()).first()
    )
    if not latest:
        return

    metric_map = {
        "reduce_blood_sugar": latest.blood_glucose,
        "reduce_bp": latest.systolic_bp,
        "improve_heart_health": latest.heart_rate,
        "improve_sleep": latest.sleep_hours,
        "drink_water": latest.water_intake_liters,
        "exercise_daily": latest.exercise_minutes,
        "lose_weight": latest.weight_kg,
    }

    changed = False
    for goal in goals:
        if goal.status != "active":
            continue
        metric_val = metric_map.get(goal.goal_type)
        if metric_val is not None:
            goal.current_value = float(metric_val)
            goal.progress_pct = goal.calc_progress()
            # Check badge
            badge = ExtendedAgentService.check_goal_badge(goal.goal_type, goal.progress_pct)
            if badge and not goal.badge_earned:
                goal.badge_earned = badge
                goal.badge_earned_at = datetime.utcnow()
            changed = True
    if changed:
        db.session.commit()


def _refresh_coaching(patient, goal: HealthGoal):
    """Generate fresh AI coaching for a goal."""
    records = (
        HealthRecord.query.filter_by(patient_id=patient.id)
        .order_by(HealthRecord.recorded_at.desc()).limit(5).all()
    )
    records_dicts = [r.to_dict() for r in reversed(records)]
    result = ExtendedAgentService.generate_goal_coaching(
        patient.to_dict(), goal.to_dict(), records_dicts
    )
    goal.ai_coaching_tip = result.get("coaching_tip", "")
    goal.motivational_message = result.get("motivational_message", "")
    goal.ai_coaching_updated = datetime.utcnow()
    db.session.commit()
