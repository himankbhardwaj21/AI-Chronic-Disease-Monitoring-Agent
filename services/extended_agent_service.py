"""
services/extended_agent_service.py — Extended AI agents for Features 1-6
All prompts stored in AGENT_INSTRUCTIONS in config.py.
"""

from config import AGENT_INSTRUCTIONS
from services.watsonx_service import WatsonxService

watsonx = WatsonxService()


class ExtendedAgentService:
    """
    New AI agents extending the base AgentService:
    - HealthReportAgent  (Feature 1) — comprehensive patient report
    - PrognosisAgent     (Feature 2) — predictive disease progression
    - ExplainAgent       (Feature 3) — explainable AI reasoning
    - EmergencyAgent     (Feature 4) — smart emergency alert analysis
    - GoalCoachAgent     (Feature 6) — health goal coaching
    """

    # ============================================================
    # FEATURE 1: COMPREHENSIVE HEALTH REPORT
    # ============================================================
    @staticmethod
    def generate_full_report(patient: dict, records: list, medications: list) -> dict:
        """Generate an enterprise-grade comprehensive health report."""
        cfg = AGENT_INSTRUCTIONS.get("health_report_agent", {})
        system_prompt = cfg.get("system_prompt", (
            "You are HealthReportAI, an expert clinical report generator powered by IBM Granite. "
            "Generate detailed, professional, patient-friendly health reports. "
            "Use clear headings, bullet points, and plain language. "
            "Always include a medical disclaimer."
        ))

        from services.agent_service import AgentService
        trend = AgentService._build_trend_summary(records[-14:] if len(records) >= 14 else records)
        avg_stats = _compute_averages(records)
        meds_text = ", ".join(m.get("name", "") + " " + m.get("dosage", "") for m in medications) or "None"
        avg_adherence = (
            sum(m.get("adherence_pct", 0) for m in medications) / len(medications)
            if medications else 0
        )

        prompt = f"""
Generate a comprehensive patient health report with ALL sections listed below.

PATIENT PROFILE:
- Name: {patient.get('name')}, Age: {patient.get('age')}, Gender: {patient.get('gender')}
- Primary Disease: {patient.get('primary_disease')}
- Secondary: {patient.get('secondary_diseases', 'None')}
- BMI: {patient.get('bmi', 'N/A')}, Blood Group: {patient.get('blood_group', 'N/A')}
- Doctor: {patient.get('doctor_name', 'N/A')}, Next Visit: {patient.get('next_appointment', 'N/A')}
- Lifestyle: Smoking: {patient.get('smoking_status', 'N/A')}, Alcohol: {patient.get('alcohol_consumption', 'N/A')}, Activity: {patient.get('activity_level', 'N/A')}
- Known Allergies: {patient.get('known_allergies', 'None')}

HEALTH DATA ({len(records)} records):
{trend}

AVERAGE STATISTICS:
- Avg Blood Glucose: {avg_stats.get('glucose', 'N/A')} mg/dL
- Avg Blood Pressure: {avg_stats.get('systolic', 'N/A')}/{avg_stats.get('diastolic', 'N/A')} mmHg
- Avg Heart Rate: {avg_stats.get('hr', 'N/A')} bpm
- Avg SpO2: {avg_stats.get('o2', 'N/A')}%
- Avg Sleep: {avg_stats.get('sleep', 'N/A')} hrs
- Avg Exercise: {avg_stats.get('exercise', 'N/A')} min/day
- Avg Stress: {avg_stats.get('stress', 'N/A')}/10

MEDICATIONS: {meds_text}
MEDICATION ADHERENCE: {avg_adherence:.1f}%

Generate the following sections with clear ## headings:

## 1. EXECUTIVE SUMMARY
(3-4 sentences overview for doctor)

## 2. CURRENT HEALTH STATUS
(overall condition assessment, key metrics)

## 3. DISEASE OVERVIEW
(status of {patient.get('primary_disease')} management)

## 4. VITAL SIGNS ANALYSIS
(each vital — current value, trend, interpretation)

## 5. BLOOD SUGAR TREND ANALYSIS
(trend over period, meaning, concerns)

## 6. BLOOD PRESSURE TREND ANALYSIS
(trend, classification, concerns)

## 7. HEART RATE ANALYSIS
(trend, rhythm concerns, cardio health)

## 8. MEDICATION ADHERENCE ANALYSIS
(adherence assessment, impact on health)

## 9. LIFESTYLE ASSESSMENT
(sleep, exercise, hydration, stress summary)

## 10. AI RISK ASSESSMENT
(overall risk level, key contributing factors)

## 11. POSSIBLE FUTURE COMPLICATIONS
(if current trends continue — list 3-5 specific risks)

## 12. PERSONALIZED LIFESTYLE RECOMMENDATIONS
(5 specific actionable changes)

## 13. DIET RECOMMENDATIONS
(disease-specific meal plan highlights)

## 14. EXERCISE RECOMMENDATIONS
(safe, specific exercise plan)

## 15. SLEEP RECOMMENDATIONS
(improvement tips based on data)

## 16. STRESS MANAGEMENT
(specific techniques for this patient)

## 17. FOLLOW-UP RECOMMENDATIONS
(tests, monitoring frequency, goals)

## 18. DOCTOR CONSULTATION SUGGESTIONS
(what to discuss at next appointment, urgency level)

Be thorough but clear. Use simple language for patient sections.
"""
        response = watsonx.generate(prompt, system_prompt, max_tokens=2000)
        return {
            "report_content": response,
            "avg_stats": avg_stats,
            "record_count": len(records),
            "med_adherence": round(avg_adherence, 1),
            "status": "success",
        }

    # ============================================================
    # FEATURE 2: PREDICTIVE DISEASE PROGRESSION
    # ============================================================
    @staticmethod
    def predict_progression(patient: dict, records: list) -> dict:
        """Predict disease progression over 7, 30, 90 days."""
        cfg = AGENT_INSTRUCTIONS.get("prognosis_agent", {})
        system_prompt = cfg.get("system_prompt", (
            "You are PrognosisAI, an expert in predictive health analytics powered by IBM Granite. "
            "Analyze historical patient data to predict disease progression. "
            "Always explain predictions in simple language with specific data evidence. "
            "Provide confidence levels and be appropriately cautious with predictions."
        ))

        from services.agent_service import AgentService
        trend = AgentService._build_trend_summary(records[-30:] if len(records) >= 30 else records)
        scores = _compute_averages(records)

        prompt = f"""
Patient: {patient.get('name')}, Age: {patient.get('age')}, Disease: {patient.get('primary_disease')}
Secondary: {patient.get('secondary_diseases', 'None')}
BMI: {patient.get('bmi', 'N/A')}, Activity: {patient.get('activity_level', 'N/A')}
Smoking: {patient.get('smoking_status', 'N/A')}

Historical Health Trend ({len(records)} records):
{trend}

Current Averages:
- Blood Glucose avg: {scores.get('glucose', 'N/A')} mg/dL
- Blood Pressure avg: {scores.get('systolic', 'N/A')}/{scores.get('diastolic', 'N/A')} mmHg
- Heart Rate avg: {scores.get('hr', 'N/A')} bpm
- Sleep avg: {scores.get('sleep', 'N/A')} hrs
- Exercise avg: {scores.get('exercise', 'N/A')} min/day

Analyze the trends and provide predictive health projections:

## OVERALL RISK SCORE
(percentage 0-100 with label: Low/Medium/High/Critical)

## 7-DAY PREDICTION
- Predicted Blood Glucose range (mg/dL)
- Predicted Blood Pressure (systolic/diastolic)
- Heart Health Trend (Improving / Stable / Declining)
- Hospitalization Risk: Low / Medium / High
- Confidence Level: X%
- Key reasoning (2-3 sentences citing specific data patterns)

## 30-DAY PREDICTION
- Predicted Blood Glucose range
- Predicted Blood Pressure
- Heart Health Trend
- Hospitalization Risk
- Predicted Weight change (kg)
- Confidence Level: X%
- Key reasoning

## 90-DAY PREDICTION
- Predicted Blood Glucose range
- Predicted Blood Pressure
- Heart Health Trend
- Hospitalization Risk
- Predicted HbA1c range (if diabetic)
- Confidence Level: X%
- Key reasoning

## MEDICATION ADHERENCE IMPACT
(How current adherence affects these predictions)

## LIFESTYLE IMPACT SCORE
(How current lifestyle affects risk: 0-100 score with explanation)

## MOST IMPORTANT INTERVENTIONS
(Top 3 specific changes that would most improve these predictions)

## WHY THESE PREDICTIONS
(Explain in simple language the specific data points that led to each prediction)

Always explain in simple terms a patient can understand.
"""
        response = watsonx.generate(prompt, system_prompt, max_tokens=1800)

        # Parse numeric risk from response for gauge display
        risk_pct = _extract_risk_percentage(response)

        return {
            "prediction_content": response,
            "risk_percentage": risk_pct,
            "record_count": len(records),
            "avg_stats": scores,
            "status": "success",
        }

    # ============================================================
    # FEATURE 3: EXPLAINABLE AI
    # ============================================================
    @staticmethod
    def explain_recommendation(patient: dict, recommendation_text: str,
                               context_records: list, context_type: str = "general") -> str:
        """
        Explain WHY an AI recommendation was made.
        Returns a patient-friendly explanation citing specific data.
        """
        cfg = AGENT_INSTRUCTIONS.get("explainable_ai", {})
        system_prompt = cfg.get("system_prompt", (
            "You are ExplainAI, a transparent AI assistant powered by IBM Granite. "
            "Your job is to explain AI health recommendations in very simple, friendly language. "
            "Always cite specific data points from the patient's records. "
            "Break down complex medical concepts into everyday language. "
            "Use analogies where helpful."
        ))

        from services.agent_service import AgentService
        recent = context_records[-7:] if len(context_records) >= 7 else context_records
        data_summary = AgentService._build_trend_summary(recent)

        prompt = f"""
Patient: {patient.get('name')}, Age: {patient.get('age')}, Disease: {patient.get('primary_disease')}

THE AI RECOMMENDATION TO EXPLAIN:
"{recommendation_text}"

PATIENT'S RECENT DATA:
{data_summary}

Please explain this recommendation in very simple language by answering:

1. WHICH SPECIFIC HEALTH METRICS led to this recommendation?
   (cite exact numbers from the data above)

2. WHY IS THE PATIENT CONSIDERED THIS RISK LEVEL?
   (explain in terms a 10-year-old could understand)

3. WHICH HISTORICAL TRENDS affected this recommendation?
   (point to specific patterns in the data)

4. WHICH LIFESTYLE FACTORS contributed?
   (sleep, exercise, diet, stress — with specific values)

5. HOW DO THE MEDICATIONS influence this?
   (impact of current adherence on the recommendation)

6. WHAT WOULD HAPPEN IF THIS IS IGNORED?
   (explain consequences simply)

7. WHAT IS THE SINGLE MOST IMPORTANT ACTION?
   (one clear, specific step the patient should take today)

Use simple, conversational language. No medical jargon.
"""
        return watsonx.generate(prompt, system_prompt, max_tokens=900)

    # ============================================================
    # FEATURE 4: EMERGENCY ALERT ANALYSIS
    # ============================================================
    @staticmethod
    def analyze_emergency(patient: dict, alert_data: dict) -> dict:
        """Generate detailed emergency alert analysis with AI explanation."""
        cfg = AGENT_INSTRUCTIONS.get("emergency_agent", {})
        system_prompt = cfg.get("system_prompt", (
            "You are EmergencyAI, an urgent medical alert specialist powered by IBM Granite. "
            "When dangerous health values are detected, provide clear, calm, actionable guidance. "
            "Always prioritize patient safety. Use numbered steps for actions. "
            "Be specific about when to call emergency services."
        ))

        metric = alert_data.get("metric", "vital sign")
        value = alert_data.get("value", "N/A")
        severity = alert_data.get("severity", "Warning")

        prompt = f"""
EMERGENCY HEALTH ALERT — {severity.upper()} LEVEL

Patient: {patient.get('name')}, Age: {patient.get('age')}
Disease: {patient.get('primary_disease')}
Secondary: {patient.get('secondary_diseases', 'None')}
Medications: {patient.get('current_medications', 'None')}
Emergency Contact: {patient.get('emergency_contact_name', 'N/A')} ({patient.get('emergency_contact_phone', 'N/A')})

DANGEROUS VALUE DETECTED:
- Metric: {metric}
- Current Value: {value}
- Severity: {severity}

Provide a complete emergency response guide:

## ALERT LEVEL
(Green/Yellow/Orange/Red/Critical with clear explanation of what this level means)

## AI EXPLANATION
(What this reading means for this patient's specific condition, in plain language — 2-3 sentences)

## POSSIBLE CAUSES
(List 3-5 most likely causes for this specific patient)

## IMMEDIATE ACTIONS — DO THIS NOW
(Numbered list of specific steps to take in the next 10 minutes)

## EMERGENCY CONTACT RECOMMENDATION
(Should they contact emergency contact? When? What to say?)

## HOSPITAL VISIT RECOMMENDATION
(Should they go to ER? Urgent care? Or manage at home? Be specific)

## WHAT TO TELL THE DOCTOR/PARAMEDIC
(Key information to communicate — current reading, symptoms, medications)

## PREVENTION FOR NEXT TIME
(2-3 specific changes to prevent recurrence)

Be calm, clear, and specific. This is urgent.
"""
        response = watsonx.generate(prompt, system_prompt, max_tokens=900)
        return {
            "explanation": response,
            "metric": metric,
            "value": value,
            "severity": severity,
            "status": "success",
        }

    # ============================================================
    # FEATURE 6: GOAL COACHING
    # ============================================================
    @staticmethod
    def generate_goal_coaching(patient: dict, goal: dict, records: list) -> dict:
        """Generate AI coaching tip and motivational message for a health goal."""
        cfg = AGENT_INSTRUCTIONS.get("goal_coach_agent", {})
        system_prompt = cfg.get("system_prompt", (
            "You are GoalCoach, an encouraging AI health goal coach powered by IBM Granite. "
            "Help patients achieve their health goals with specific, realistic advice. "
            "Be motivating, celebrate progress, and provide practical daily tips. "
            "Personalize coaching to the patient's disease, age, and current metrics."
        ))

        progress = goal.get("progress_pct", 0)
        from services.agent_service import AgentService
        recent_summary = AgentService._build_trend_summary(records[-5:] if records else [])

        prompt = f"""
Patient: {patient.get('name')}, Age: {patient.get('age')}, Disease: {patient.get('primary_disease')}

HEALTH GOAL:
- Goal: {goal.get('title')}
- Type: {goal.get('goal_type')}
- Target: {goal.get('target_value')} {goal.get('target_unit', '')}
- Starting value: {goal.get('baseline_value')}
- Current value: {goal.get('current_value')}
- Progress: {progress}%
- Days remaining: {goal.get('days_remaining', 'N/A')}

Recent Health Data:
{recent_summary}

Provide:

## COACHING TIP
(1 specific, actionable daily tip to make progress toward this goal — 2-3 sentences)

## MOTIVATIONAL MESSAGE
(Short, personalized encouragement referencing their progress — 2 sentences, warm and genuine)

## TODAY'S MICRO-GOAL
(One tiny achievable action for today that moves toward the bigger goal)

## PROGRESS ANALYSIS
(What the {progress}% progress means, what's working, what to adjust)

Keep it warm, personal, and achievable. Reference the patient by name.
"""
        response = watsonx.generate(prompt, system_prompt, max_tokens=500)

        # Parse sections from response
        coaching_tip = _extract_section(response, "COACHING TIP")
        motivational = _extract_section(response, "MOTIVATIONAL MESSAGE")

        return {
            "coaching_tip": coaching_tip or response[:300],
            "motivational_message": motivational or "",
            "full_response": response,
            "status": "success",
        }

    # ============================================================
    # GOAL BADGE LOGIC
    # ============================================================
    @staticmethod
    def check_goal_badge(goal_type: str, progress: float) -> str:
        """Return badge name if earned."""
        if progress >= 100:
            badges = {
                "reduce_blood_sugar": "Sugar Champion",
                "reduce_bp": "BP Warrior",
                "lose_weight": "Weight Hero",
                "improve_sleep": "Sleep Master",
                "drink_water": "Hydration Star",
                "exercise_daily": "Fitness Champion",
                "improve_heart_health": "Heart Guardian",
                "custom": "Goal Achiever",
            }
            return badges.get(goal_type, "Goal Achiever")
        if progress >= 75:
            return "Almost There"
        if progress >= 50:
            return "Halfway Hero"
        if progress >= 25:
            return "Good Start"
        return None


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _compute_averages(records: list) -> dict:
    """Compute average vital stats from a list of record dicts."""
    if not records:
        return {}

    def avg(key):
        vals = [r.get(key) for r in records if r.get(key) is not None]
        return round(sum(vals) / len(vals), 1) if vals else None

    return {
        "glucose": avg("blood_glucose"),
        "systolic": avg("systolic_bp"),
        "diastolic": avg("diastolic_bp"),
        "hr": avg("heart_rate"),
        "o2": avg("oxygen_saturation"),
        "temp": avg("body_temperature"),
        "sleep": avg("sleep_hours"),
        "exercise": avg("exercise_minutes"),
        "stress": avg("stress_level"),
        "weight": avg("weight_kg"),
        "health_score": avg("health_score"),
    }


def _extract_risk_percentage(text: str) -> int:
    """Extract a risk percentage from AI text output."""
    import re
    matches = re.findall(r'(\d{1,3})\s*%', text)
    for m in matches:
        val = int(m)
        if 0 <= val <= 100:
            return val
    # Fallback: map keywords
    text_lower = text.lower()
    if "critical" in text_lower:
        return 85
    if "high risk" in text_lower:
        return 65
    if "medium risk" in text_lower or "moderate" in text_lower:
        return 42
    return 22


def _extract_section(text: str, section_name: str) -> str:
    """Extract a named section from AI response text."""
    import re
    pattern = rf"##\s+{re.escape(section_name)}[^\n]*\n(.*?)(?=##|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
