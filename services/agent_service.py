"""
services/agent_service.py — Multi-Agent AI system
Orchestrates all 5 specialized health agents using IBM Granite.
"""

import json
from config import AGENT_INSTRUCTIONS
from services.watsonx_service import WatsonxService

watsonx = WatsonxService()


class AgentService:
    """
    Orchestrates the 5 specialized ChronicCare AI agents:
    1. Health Monitoring Agent (VitalGuard)
    2. Risk Prediction Agent (RiskSense AI)
    3. Medication Assistant Agent (MedCoach)
    4. Lifestyle Recommendation Agent (WellnessCoach)
    5. Medical Report Agent (ReportMD)
    """

    # ============================================================
    # AGENT 1: Health Monitoring Agent
    # ============================================================
    @staticmethod
    def analyze_vitals(patient: dict, health_record: dict) -> dict:
        """
        VitalGuard: Analyze vital signs and detect abnormalities.
        Returns structured analysis with severity flags.
        """
        cfg = AGENT_INSTRUCTIONS["health_monitoring_agent"]
        thresholds = AGENT_INSTRUCTIONS["alert_thresholds"]

        # Build context prompt
        prompt = f"""
Patient Profile:
- Name: {patient.get('name', 'N/A')}
- Age: {patient.get('age', 'N/A')} | Gender: {patient.get('gender', 'N/A')}
- Primary Disease: {patient.get('primary_disease', 'N/A')}
- Secondary Conditions: {patient.get('secondary_diseases', 'None')}
- Current Medications: {patient.get('current_medications', 'None')}

Latest Vital Signs:
- Blood Glucose: {health_record.get('blood_glucose', 'N/A')} mg/dL
- Blood Pressure: {health_record.get('systolic_bp', 'N/A')}/{health_record.get('diastolic_bp', 'N/A')} mmHg
- Heart Rate: {health_record.get('heart_rate', 'N/A')} bpm
- Oxygen Saturation: {health_record.get('oxygen_saturation', 'N/A')}%
- Body Temperature: {health_record.get('body_temperature', 'N/A')}°C
- Weight: {health_record.get('weight_kg', 'N/A')} kg | BMI: {health_record.get('bmi', 'N/A')}

Symptoms Reported: {health_record.get('symptoms', 'None')}

Normal Reference Ranges:
- Blood Pressure: <120/80 mmHg (Normal), 130-139/80-89 (Stage 1 High), ≥140/90 (Stage 2 High)
- Blood Glucose (fasting): 70-100 mg/dL (Normal), 100-125 (Prediabetes), ≥126 (Diabetes)
- Heart Rate: 60-100 bpm (Normal)
- Oxygen Saturation: ≥95% (Normal), <90% (Critical)
- Temperature: 36.1-37.2°C (Normal), ≥38°C (Fever)

Provide a comprehensive vital signs analysis. For each vital, state:
1. Current value vs normal range
2. Status: Normal / Warning / Critical
3. What this means for the patient in plain language
4. Immediate action if abnormal

Then provide an overall health assessment and a daily health score (0-100).
Format clearly with sections for each vital sign.
"""
        response = watsonx.generate(prompt, cfg["system_prompt"])
        health_score = AgentService._calculate_health_score(health_record)
        alerts = AgentService._detect_vital_alerts(patient, health_record, thresholds)

        return {
            "agent": cfg["name"],
            "analysis": response,
            "health_score": health_score,
            "alerts": alerts,
            "status": "success",
        }

    # ============================================================
    # AGENT 2: Risk Prediction Agent
    # ============================================================
    @staticmethod
    def predict_risk(patient: dict, health_records: list) -> dict:
        """
        RiskSense AI: Predict disease progression and risk level.
        Returns risk score, risk factors, and predictions.
        """
        cfg = AGENT_INSTRUCTIONS["risk_prediction_agent"]

        # Build trend summary from last records
        recent = health_records[-7:] if len(health_records) >= 7 else health_records
        trend_summary = AgentService._build_trend_summary(recent)

        prompt = f"""
Patient Profile:
- Name: {patient.get('name')}, Age: {patient.get('age')}, Gender: {patient.get('gender')}
- Primary Disease: {patient.get('primary_disease')}
- Secondary Conditions: {patient.get('secondary_diseases', 'None')}
- Smoking: {patient.get('smoking_status', 'N/A')} | Alcohol: {patient.get('alcohol_consumption', 'N/A')}
- Activity Level: {patient.get('activity_level', 'N/A')}
- BMI: {patient.get('bmi', 'N/A')}

Health Trends (Last {len(recent)} records):
{trend_summary}

Based on this data, provide:

1. OVERALL RISK SCORE: Low / Medium / High / Critical
   (with percentage confidence e.g. "High Risk — 78% confidence")

2. TOP RISK FACTORS (list 3-5 specific factors from the data)

3. DISEASE PROGRESSION: Is the condition improving, stable, or worsening?
   Provide evidence from the trends.

4. PREDICTED COMPLICATIONS (next 30-90 days if trends continue):
   List specific complications possible for {patient.get('primary_disease')}

5. EMERGENCY WARNING SIGNS to watch for

6. PREVENTIVE INTERVENTIONS (top 3 most impactful actions to reduce risk)

7. DOCTOR VISIT URGENCY: Routine / Soon (within 2 weeks) / Urgent (within 48hrs) / Emergency

Be specific, evidence-based, and use simple language for the patient.
"""
        response = watsonx.generate(prompt, cfg["system_prompt"])
        risk_score = AgentService._calculate_risk_score(patient, health_records)

        return {
            "agent": cfg["name"],
            "analysis": response,
            "risk_level": risk_score["level"],
            "risk_percentage": risk_score["percentage"],
            "risk_factors": risk_score["factors"],
            "status": "success",
        }

    # ============================================================
    # AGENT 3: Medication Assistant Agent
    # ============================================================
    @staticmethod
    def medication_guidance(patient: dict, medications: list) -> dict:
        """
        MedCoach: Provide medication management guidance.
        Returns adherence analysis and personalized guidance.
        """
        cfg = AGENT_INSTRUCTIONS["medication_agent"]

        med_summary = "\n".join([
            f"- {m.get('name', 'N/A')} {m.get('dosage', '')} — {m.get('frequency', '')} "
            f"(Adherence: {m.get('adherence_pct', 0)}%, Last taken: {m.get('last_taken', 'Unknown')})"
            for m in medications
        ]) or "No medications recorded."

        avg_adherence = (
            sum(m.get("adherence_pct", 0) for m in medications) / len(medications)
            if medications else 0
        )

        prompt = f"""
Patient: {patient.get('name')}, Age: {patient.get('age')}
Disease: {patient.get('primary_disease')}

Current Medication Regimen:
{med_summary}

Overall Medication Adherence: {avg_adherence:.1f}%

Provide:
1. ADHERENCE ASSESSMENT: Rate adherence as Excellent (>90%) / Good (75-90%) / Fair (50-75%) / Poor (<50%)
   Explain what current adherence means for disease management.

2. MEDICATION-BY-MEDICATION GUIDANCE:
   For each medication, explain:
   - What it does (in simple terms)
   - Why adherence is critical for this disease
   - What happens if doses are missed
   - Best time/way to take it

3. MISSED DOSE PROTOCOL: What to do if a dose is missed for each medication

4. PRACTICAL TIPS to improve adherence:
   List 4-5 specific, actionable strategies

5. UPCOMING REMINDERS: Suggest a daily medication schedule

6. WARNING SIGNS of under-medication to watch for

Keep language simple, encouraging, and non-judgmental.
"""
        response = watsonx.generate(prompt, cfg["system_prompt"])
        return {
            "agent": cfg["name"],
            "analysis": response,
            "adherence_score": round(avg_adherence, 1),
            "medications": medications,
            "status": "success",
        }

    # ============================================================
    # AGENT 4: Lifestyle Recommendation Agent
    # ============================================================
    @staticmethod
    def lifestyle_recommendations(patient: dict, latest_record: dict) -> dict:
        """
        WellnessCoach: Generate personalized lifestyle recommendations.
        """
        cfg = AGENT_INSTRUCTIONS["lifestyle_agent"]

        prompt = f"""
Patient Profile:
- Name: {patient.get('name')}, Age: {patient.get('age')}, Gender: {patient.get('gender')}
- Disease: {patient.get('primary_disease')}
- BMI: {patient.get('bmi', 'N/A')} | Weight: {patient.get('weight_kg', 'N/A')} kg
- Activity Level: {patient.get('activity_level', 'Sedentary')}
- Smoking: {patient.get('smoking_status', 'N/A')}
- Alcohol: {patient.get('alcohol_consumption', 'N/A')}

Recent Health Metrics:
- Sleep: {latest_record.get('sleep_hours', 'N/A')} hours/night
- Water Intake: {latest_record.get('water_intake_liters', 'N/A')} liters/day
- Exercise: {latest_record.get('exercise_minutes', 'N/A')} minutes/day
- Stress Level: {latest_record.get('stress_level', 'N/A')}/10
- Mood: {latest_record.get('mood', 'N/A')}
- Steps: {latest_record.get('steps_count', 'N/A')}/day
- Calories Burned: {latest_record.get('calories_burned', 'N/A')}

Provide a PERSONALIZED LIFESTYLE PLAN:

1. NUTRITION PLAN (disease-specific for {patient.get('primary_disease')}):
   - Foods to eat more of (5 specific items with reasons)
   - Foods to avoid (5 specific items with reasons)
   - Meal timing recommendations
   - Sample daily meal plan

2. EXERCISE PROGRAM (safe for their condition):
   - Recommended exercise types
   - Duration and frequency
   - How to start safely
   - Warning signs to stop exercising

3. SLEEP OPTIMIZATION:
   - Current vs recommended hours
   - 4 specific tips to improve sleep quality

4. HYDRATION GOALS:
   - Daily water target
   - 3 practical ways to stay hydrated

5. STRESS MANAGEMENT:
   - Current stress level assessment
   - 3 specific techniques for this patient

6. WEIGHT MANAGEMENT (if BMI indicates need):
   - Safe weight loss/maintenance strategies

7. WEEKLY WELLNESS GOALS (achievable 7-day targets)

Be specific, motivating, and realistic for a {patient.get('age')}-year-old with {patient.get('primary_disease')}.
"""
        response = watsonx.generate(prompt, cfg["system_prompt"], max_tokens=1200)
        return {
            "agent": cfg["name"],
            "recommendations": response,
            "wellness_score": AgentService._calculate_wellness_score(latest_record),
            "status": "success",
        }

    # ============================================================
    # AGENT 5: Medical Report Agent
    # ============================================================
    @staticmethod
    def generate_report(patient: dict, health_records: list, medications: list,
                        report_type: str = "weekly") -> dict:
        """
        ReportMD: Generate comprehensive medical report.
        report_type: 'daily' | 'weekly' | 'monthly'
        """
        cfg = AGENT_INSTRUCTIONS["report_agent"]

        period_records = AgentService._get_period_records(health_records, report_type)
        trend_summary = AgentService._build_trend_summary(period_records)
        avg_health_score = (
            sum(r.get("health_score", 0) or 0 for r in period_records) / len(period_records)
            if period_records else 0
        )

        prompt = f"""
Generate a professional {report_type.upper()} HEALTH REPORT for:

PATIENT: {patient.get('name')} | Age: {patient.get('age')} | Disease: {patient.get('primary_disease')}
Doctor: {patient.get('doctor_name', 'N/A')} | Report Period: Last {report_type}

HEALTH DATA SUMMARY ({len(period_records)} records):
{trend_summary}

Average Health Score: {avg_health_score:.1f}/100

MEDICATIONS: {', '.join([m.get('name', '') for m in medications]) or 'None'}

Generate a comprehensive report with these sections:

1. EXECUTIVE HEALTH SUMMARY (2-3 sentences for quick review)

2. VITAL SIGNS ANALYSIS
   - Blood Pressure trend (improving/stable/worsening with values)
   - Blood Glucose trend
   - Heart Rate summary
   - Oxygen Saturation
   - Notable changes this {report_type}

3. DISEASE MANAGEMENT ASSESSMENT
   - How well is {patient.get('primary_disease')} being managed?
   - Progress vs previous {report_type}
   - Key concerns

4. MEDICATION ADHERENCE SUMMARY

5. LIFESTYLE METRICS REVIEW
   - Sleep, exercise, nutrition, hydration summary

6. RISK ASSESSMENT
   - Current risk level and trend
   - Top 3 risk factors identified

7. AI RECOMMENDATIONS FOR PATIENT (plain language)
   - Top 5 priority actions

8. NOTES FOR DR. {patient.get('doctor_name', 'PHYSICIAN')} (clinical language)
   - Items requiring physician attention
   - Suggested tests or interventions

9. HEALTH GOALS FOR NEXT {report_type.upper()}

Format professionally. Use clear section headers.
"""
        response = watsonx.generate(prompt, cfg["system_prompt"], max_tokens=1500)
        return {
            "agent": cfg["name"],
            "report_type": report_type,
            "report_content": response,
            "period_records": len(period_records),
            "avg_health_score": round(avg_health_score, 1),
            "generated_at": AgentService._now_str(),
            "status": "success",
        }

    # ============================================================
    # Chat Assistant
    # ============================================================
    @staticmethod
    def chat_response(patient: dict, conversation_history: list, user_message: str) -> str:
        """CareBot: Handle patient chat queries."""
        cfg = AGENT_INSTRUCTIONS["chat_assistant"]

        system_prompt = (
            f"{cfg['system_prompt']}\n\n"
            f"Current Patient: {patient.get('name', 'Unknown Patient')}, "
            f"Age: {patient.get('age', 'N/A')}, "
            f"Disease: {patient.get('primary_disease', 'N/A')}. "
            f"Personalize all responses for this patient."
        )

        messages = list(conversation_history)
        messages.append({"role": "user", "content": user_message})

        return watsonx.chat(messages, system_prompt)

    # ============================================================
    # Smart Health Insights
    # ============================================================
    @staticmethod
    def generate_insights(patient: dict, health_records: list) -> dict:
        """Generate top health insights and trends."""
        if not health_records:
            return {"insights": [], "status": "no_data"}

        trend = AgentService._build_trend_summary(health_records[-10:])
        prompt = f"""
Patient: {patient.get('name')}, Disease: {patient.get('primary_disease')}

Recent Health Trend:
{trend}

Generate a concise health insights report:

1. TOP 5 HEALTH IMPROVEMENTS this period (be specific with data)
2. TOP 3 CONCERNS OR NEGATIVE TRENDS (with data evidence)
3. PREDICTED COMPLICATIONS if current trends continue
4. TOP 3 PREVENTIVE ACTIONS (most impactful interventions)
5. WELLNESS TIPS personalized for this patient
6. ONE MOTIVATIONAL MESSAGE for the patient

Keep each point to 1-2 sentences. Be specific and data-driven.
"""
        response = watsonx.generate(prompt)
        return {"insights": response, "status": "success"}

    # ============================================================
    # Internal Helpers
    # ============================================================
    @staticmethod
    def _calculate_health_score(record: dict) -> float:
        """Calculate composite health score 0-100."""
        score = 100.0
        # Blood pressure penalty
        systolic = record.get("systolic_bp") or 0
        if systolic >= 180:
            score -= 25
        elif systolic >= 140:
            score -= 15
        elif systolic >= 130:
            score -= 8

        # Blood glucose penalty
        glucose = record.get("blood_glucose") or 0
        if glucose >= 250:
            score -= 20
        elif glucose >= 180:
            score -= 12
        elif glucose < 70 and glucose > 0:
            score -= 15

        # Heart rate
        hr = record.get("heart_rate") or 0
        if hr > 130 or hr < 50 and hr > 0:
            score -= 15
        elif hr > 100:
            score -= 8

        # Oxygen
        o2 = record.get("oxygen_saturation") or 0
        if o2 < 90 and o2 > 0:
            score -= 20
        elif o2 < 94 and o2 > 0:
            score -= 10

        # Lifestyle bonuses/penalties
        sleep = record.get("sleep_hours") or 0
        if 7 <= sleep <= 9:
            score += 3
        elif sleep < 5:
            score -= 8

        exercise = record.get("exercise_minutes") or 0
        if exercise >= 30:
            score += 5
        elif exercise == 0:
            score -= 5

        stress = record.get("stress_level") or 0
        if stress >= 8:
            score -= 10
        elif stress <= 3:
            score += 3

        return max(0, min(100, round(score, 1)))

    @staticmethod
    def _calculate_risk_score(patient: dict, records: list) -> dict:
        """Calculate overall risk score and identify top risk factors."""
        factors = []
        score = 0

        recent = records[-3:] if len(records) >= 3 else records
        if not recent:
            return {"level": "Unknown", "percentage": 0, "factors": []}

        # Average key vitals
        avg_sys = sum(r.get("systolic_bp") or 0 for r in recent) / len(recent)
        avg_glucose = sum(r.get("blood_glucose") or 0 for r in recent) / len(recent)
        avg_o2 = sum(r.get("oxygen_saturation") or 100 for r in recent) / len(recent)
        avg_stress = sum(r.get("stress_level") or 0 for r in recent) / len(recent)

        if avg_sys >= 160:
            score += 30
            factors.append(f"Severely elevated blood pressure (avg {avg_sys:.0f} mmHg)")
        elif avg_sys >= 140:
            score += 20
            factors.append(f"High blood pressure (avg {avg_sys:.0f} mmHg)")
        elif avg_sys >= 130:
            score += 10
            factors.append(f"Elevated blood pressure (avg {avg_sys:.0f} mmHg)")

        if avg_glucose >= 250:
            score += 30
            factors.append(f"Critically high blood glucose (avg {avg_glucose:.0f} mg/dL)")
        elif avg_glucose >= 180:
            score += 20
            factors.append(f"High blood glucose (avg {avg_glucose:.0f} mg/dL)")

        if avg_o2 < 90:
            score += 25
            factors.append(f"Critical oxygen saturation (avg {avg_o2:.1f}%)")
        elif avg_o2 < 94:
            score += 15
            factors.append(f"Low oxygen saturation (avg {avg_o2:.1f}%)")

        if avg_stress >= 8:
            score += 15
            factors.append(f"High chronic stress level (avg {avg_stress:.1f}/10)")

        bmi = patient.get("bmi")
        if bmi and bmi >= 35:
            score += 15
            factors.append(f"Severe obesity (BMI {bmi})")
        elif bmi and bmi >= 30:
            score += 10
            factors.append(f"Obesity (BMI {bmi})")

        if patient.get("smoking_status") == "Current":
            score += 10
            factors.append("Active smoker")

        pct = min(100, score)
        if pct >= 70:
            level = "Critical"
        elif pct >= 45:
            level = "High"
        elif pct >= 25:
            level = "Medium"
        else:
            level = "Low"

        return {"level": level, "percentage": pct, "factors": factors}

    @staticmethod
    def _calculate_wellness_score(record: dict) -> float:
        """Calculate lifestyle wellness score 0-100."""
        score = 50.0
        sleep = record.get("sleep_hours") or 0
        if 7 <= sleep <= 9:
            score += 15
        elif sleep >= 6:
            score += 8
        elif sleep < 5:
            score -= 10

        water = record.get("water_intake_liters") or 0
        if water >= 2.5:
            score += 15
        elif water >= 2:
            score += 8
        elif water < 1.5:
            score -= 10

        exercise = record.get("exercise_minutes") or 0
        if exercise >= 45:
            score += 20
        elif exercise >= 30:
            score += 12
        elif exercise >= 15:
            score += 6
        else:
            score -= 5

        stress = record.get("stress_level") or 5
        score += (10 - stress) * 1.5

        return max(0, min(100, round(score, 1)))

    @staticmethod
    def _detect_vital_alerts(patient: dict, record: dict, thresholds: dict) -> list:
        """Auto-detect alert conditions from vital signs."""
        alerts = []
        name = patient.get("name", "Patient")

        # Blood pressure
        systolic = record.get("systolic_bp") or 0
        diastolic = record.get("diastolic_bp") or 0
        if systolic >= thresholds["blood_pressure_systolic_critical"]:
            alerts.append({
                "severity": "Critical",
                "title": "Hypertensive Crisis",
                "message": f"Blood pressure {systolic}/{diastolic} mmHg is dangerously high.",
                "action": "Seek emergency medical care immediately. Call 112/911.",
                "triggered_by": "blood_pressure",
            })
        elif systolic >= thresholds["blood_pressure_systolic_high"]:
            alerts.append({
                "severity": "Warning",
                "title": "High Blood Pressure",
                "message": f"Blood pressure {systolic}/{diastolic} mmHg exceeds safe range.",
                "action": "Rest, reduce stress, take medication as prescribed. Contact doctor today.",
                "triggered_by": "blood_pressure",
            })

        # Blood glucose
        glucose = record.get("blood_glucose") or 0
        if glucose >= thresholds["blood_glucose_critical"]:
            alerts.append({
                "severity": "Critical",
                "title": "Critically High Blood Sugar",
                "message": f"Blood glucose {glucose} mg/dL is critically elevated.",
                "action": "Contact your doctor or go to emergency. Check ketones if T1DM.",
                "triggered_by": "blood_glucose",
            })
        elif glucose >= thresholds["blood_glucose_high"]:
            alerts.append({
                "severity": "Warning",
                "title": "Elevated Blood Sugar",
                "message": f"Blood glucose {glucose} mg/dL is above target range.",
                "action": "Review recent meals, take medications as prescribed, increase water intake.",
                "triggered_by": "blood_glucose",
            })
        elif 0 < glucose < thresholds["blood_glucose_low"]:
            alerts.append({
                "severity": "Critical",
                "title": "Low Blood Sugar (Hypoglycemia)",
                "message": f"Blood glucose {glucose} mg/dL is dangerously low.",
                "action": "Consume 15g fast carbs immediately (juice/glucose tablets). Recheck in 15 min.",
                "triggered_by": "blood_glucose",
            })

        # Oxygen
        o2 = record.get("oxygen_saturation") or 0
        if 0 < o2 < thresholds["oxygen_saturation_critical"]:
            alerts.append({
                "severity": "Emergency",
                "title": "Critical Oxygen Level",
                "message": f"Oxygen saturation {o2}% is critically low.",
                "action": "Call emergency services (112/911) immediately.",
                "triggered_by": "oxygen_saturation",
            })
        elif 0 < o2 < thresholds["oxygen_saturation_low"]:
            alerts.append({
                "severity": "Warning",
                "title": "Low Oxygen Saturation",
                "message": f"Oxygen saturation {o2}% is below normal.",
                "action": "Rest, practice deep breathing, contact doctor if persistent.",
                "triggered_by": "oxygen_saturation",
            })

        # Heart rate
        hr = record.get("heart_rate") or 0
        if hr >= thresholds["heart_rate_critical"]:
            alerts.append({
                "severity": "Warning",
                "title": "Rapid Heart Rate (Tachycardia)",
                "message": f"Heart rate {hr} bpm is unusually high.",
                "action": "Rest immediately. If with chest pain/dizziness, seek emergency care.",
                "triggered_by": "heart_rate",
            })
        elif 0 < hr < thresholds["heart_rate_low"]:
            alerts.append({
                "severity": "Warning",
                "title": "Slow Heart Rate (Bradycardia)",
                "message": f"Heart rate {hr} bpm is below normal.",
                "action": "Contact your doctor, especially if feeling dizzy or fainting.",
                "triggered_by": "heart_rate",
            })

        # Stress
        stress = record.get("stress_level") or 0
        if stress >= thresholds["stress_level_high"]:
            alerts.append({
                "severity": "Info",
                "title": "High Stress Level Detected",
                "message": f"Stress level {stress}/10 is significantly elevated.",
                "action": "Practice deep breathing, mindfulness, or take a short break.",
                "triggered_by": "stress_level",
            })

        return alerts

    @staticmethod
    def _build_trend_summary(records: list) -> str:
        """Build a text summary of health trends from records list."""
        if not records:
            return "No records available."

        lines = []
        for r in records:
            date = r.get("recorded_at", "N/A")
            lines.append(
                f"[{date}] "
                f"BP:{r.get('systolic_bp','?')}/{r.get('diastolic_bp','?')} "
                f"Glucose:{r.get('blood_glucose','?')}mg/dL "
                f"HR:{r.get('heart_rate','?')}bpm "
                f"O2:{r.get('oxygen_saturation','?')}% "
                f"Sleep:{r.get('sleep_hours','?')}h "
                f"Exercise:{r.get('exercise_minutes','?')}min "
                f"Stress:{r.get('stress_level','?')}/10 "
                f"Score:{r.get('health_score','?')}"
            )
        return "\n".join(lines)

    @staticmethod
    def _get_period_records(records: list, report_type: str) -> list:
        """Filter records for the report period."""
        counts = {"daily": 1, "weekly": 7, "monthly": 30}
        count = counts.get(report_type, 7)
        return records[-count:] if len(records) >= count else records

    @staticmethod
    def _now_str() -> str:
        from datetime import datetime
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
