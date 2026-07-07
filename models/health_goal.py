"""
models/health_goal.py — Patient health goals model (Feature 6)
"""

from datetime import datetime
from app_factory import db


class HealthGoal(db.Model):
    __tablename__ = "health_goals"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    # Goal definition
    goal_type = db.Column(db.String(60), nullable=False)
    # Types: reduce_blood_sugar | reduce_bp | lose_weight | improve_sleep |
    #        drink_water | exercise_daily | improve_heart_health | custom

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(40), default="bi-trophy")
    color = db.Column(db.String(20), default="primary")

    # Target values
    target_value = db.Column(db.Float)           # e.g. 130 (systolic), 75 (kg)
    target_unit = db.Column(db.String(20))       # mg/dL, kg, hrs, min, L
    baseline_value = db.Column(db.Float)         # starting value
    current_value = db.Column(db.Float)          # latest measured value

    # Time tracking
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    target_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Status
    status = db.Column(db.String(20), default="active")  # active | completed | paused | failed
    progress_pct = db.Column(db.Float, default=0.0)

    # AI coaching
    ai_coaching_tip = db.Column(db.Text)
    ai_coaching_updated = db.Column(db.DateTime)
    motivational_message = db.Column(db.Text)

    # Badge / achievement
    badge_earned = db.Column(db.String(60))
    badge_earned_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calc_progress(self) -> float:
        """Calculate goal progress percentage."""
        if self.baseline_value is None or self.target_value is None:
            return self.progress_pct or 0.0
        total_change = abs(self.target_value - self.baseline_value)
        if total_change == 0:
            return 100.0
        current = self.current_value if self.current_value is not None else self.baseline_value
        made = abs(current - self.baseline_value)
        pct = min(100.0, (made / total_change) * 100)
        return round(pct, 1)

    def days_remaining(self) -> int:
        if not self.target_date:
            return None
        delta = self.target_date - datetime.utcnow()
        return max(0, delta.days)

    def to_dict(self):
        return {
            "id": self.id,
            "goal_type": self.goal_type,
            "title": self.title,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "target_value": self.target_value,
            "target_unit": self.target_unit,
            "baseline_value": self.baseline_value,
            "current_value": self.current_value,
            "target_date": self.target_date.strftime("%Y-%m-%d") if self.target_date else None,
            "status": self.status,
            "progress_pct": self.calc_progress(),
            "days_remaining": self.days_remaining(),
            "ai_coaching_tip": self.ai_coaching_tip,
            "motivational_message": self.motivational_message,
            "badge_earned": self.badge_earned,
        }

    def __repr__(self):
        return f"<HealthGoal [{self.goal_type}] {self.title}>"
