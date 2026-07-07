"""
config.py — ChronicCare AI Application Configuration
Loads all settings from environment variables (.env file).
Credentials are NEVER hardcoded — always loaded from .env.
Includes AGENT_INSTRUCTIONS for easy AI customization.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# FLASK CONFIGURATION
# ============================================================
class Config:
    # Security — MUST be set in .env for production
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///data/chroniccare.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Forms & Security
    WTF_CSRF_ENABLED = os.getenv("WTF_CSRF_ENABLED", "True") == "True"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Server
    PORT = int(os.getenv("PORT", 5000))

    # Max upload / request size
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = logging.WARNING

    # Stricter security in production
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = "https"


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = logging.ERROR


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig,
}


# ============================================================
# PRODUCTION LOGGING SETUP
# ============================================================
def configure_logging(app):
    """Configure structured logging for the Flask application."""
    env = os.getenv("FLASK_ENV", "development")
    level = logging.WARNING if env == "production" else logging.DEBUG

    # Root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Suppress noisy third-party loggers in production
    if env == "production":
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    app.logger.setLevel(level)
    if not app.debug:
        app.logger.info("ChronicCare AI started in %s mode", env)


# ============================================================
# IBM watsonx.ai CONFIGURATION
# ============================================================
WATSONX_CONFIG = {
    "api_key": os.getenv("IBM_API_KEY", ""),
    "project_id": os.getenv("IBM_PROJECT_ID", ""),
    "url": os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
    "model_id": os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-8b-instruct"),
    "region": os.getenv("IBM_REGION", "us-south"),
    "parameters": {
        "max_new_tokens": int(os.getenv("MAX_TOKENS", 1024)),
        "temperature": float(os.getenv("TEMPERATURE", 0.7)),
        "top_p": float(os.getenv("TOP_P", 0.9)),
        "top_k": int(os.getenv("TOP_K", 50)),
        "repetition_penalty": 1.1,
        "stop_sequences": ["Human:", "User:"],
    },
}


# ============================================================
# AGENT INSTRUCTIONS — Easily customizable AI behavior
# ============================================================
AGENT_INSTRUCTIONS = {

    # ----------------------------------------------------------
    # GLOBAL SETTINGS
    # ----------------------------------------------------------
    "language": "English",
    "response_tone": "empathetic, professional, clear, and reassuring",
    "response_style": "structured with bullet points, short paragraphs, and clear headings",
    "explanation_mode": "simple language suitable for patients with no medical background",

    # ----------------------------------------------------------
    # SUPPORTED DISEASES
    # ----------------------------------------------------------
    "supported_diseases": [
        "Type 2 Diabetes",
        "Type 1 Diabetes",
        "Hypertension",
        "Heart Disease",
        "Coronary Artery Disease",
        "Obesity",
        "Chronic Kidney Disease",
        "Asthma",
        "COPD",
        "Arthritis",
    ],

    # ----------------------------------------------------------
    # MEDICAL SAFETY RULES
    # ----------------------------------------------------------
    "safety_rules": [
        "Always recommend consulting a licensed physician for diagnosis",
        "Never suggest stopping prescribed medications without doctor approval",
        "Always escalate life-threatening symptoms to emergency services",
        "Do not provide specific dosage amounts without doctor verification",
        "Include disclaimer: 'This is AI guidance, not medical advice'",
        "Prioritize patient safety above all recommendations",
    ],

    # ----------------------------------------------------------
    # ALERT SENSITIVITY THRESHOLDS
    # ----------------------------------------------------------
    "alert_thresholds": {
        "blood_pressure_systolic_high": 140,
        "blood_pressure_systolic_critical": 180,
        "blood_pressure_diastolic_high": 90,
        "blood_pressure_diastolic_critical": 120,
        "blood_glucose_low": 70,
        "blood_glucose_high": 180,
        "blood_glucose_critical": 250,
        "heart_rate_low": 50,
        "heart_rate_high": 100,
        "heart_rate_critical": 130,
        "oxygen_saturation_low": 94,
        "oxygen_saturation_critical": 90,
        "temperature_high": 38.0,
        "temperature_critical": 39.5,
        "bmi_overweight": 25.0,
        "bmi_obese": 30.0,
        "stress_level_high": 7,
    },

    # ----------------------------------------------------------
    # AGENT 1: HEALTH MONITORING AGENT
    # ----------------------------------------------------------
    "health_monitoring_agent": {
        "name": "VitalGuard",
        "personality": "precise, data-driven, vigilant health monitor",
        "system_prompt": (
            "You are VitalGuard, an AI health monitoring specialist. "
            "Analyze the patient's vital signs and health metrics with clinical precision. "
            "Identify abnormal values, explain what they mean in simple terms, "
            "and provide clear next steps. Always note severity level (Normal/Warning/Critical). "
            "Be factual and reassuring, avoiding unnecessary alarm."
        ),
        "focus_areas": [
            "Blood glucose analysis",
            "Blood pressure interpretation",
            "Heart rate and rhythm",
            "Oxygen saturation",
            "Body temperature",
            "BMI and weight trends",
            "Vital sign correlations",
        ],
    },

    # ----------------------------------------------------------
    # AGENT 2: RISK PREDICTION AGENT
    # ----------------------------------------------------------
    "risk_prediction_agent": {
        "name": "RiskSense AI",
        "personality": "analytical, predictive, proactive risk assessor",
        "system_prompt": (
            "You are RiskSense AI, a predictive health risk analyst. "
            "Based on patient data, predict disease progression and identify risk factors. "
            "Generate a clear risk score (Low/Medium/High/Critical) with detailed explanations. "
            "Identify early warning signs and recommend preventive interventions. "
            "Use evidence-based reasoning and cite which specific data points raised the risk."
        ),
        "risk_factors": [
            "Disease progression indicators",
            "Vital sign trends",
            "Medication adherence",
            "Lifestyle factors",
            "Comorbidity risks",
            "Emergency condition prediction",
        ],
    },

    # ----------------------------------------------------------
    # AGENT 3: MEDICATION ASSISTANT AGENT
    # ----------------------------------------------------------
    "medication_agent": {
        "name": "MedCoach",
        "personality": "organized, helpful, safety-focused medication guide",
        "system_prompt": (
            "You are MedCoach, an AI medication management assistant. "
            "Help patients understand their medications, track adherence, "
            "and provide reminders. Explain drug purposes in plain language. "
            "Identify potential issues with missed doses and suggest safe practices. "
            "Always emphasize consulting the prescribing doctor for dosage changes. "
            "Be encouraging and non-judgmental about missed medications."
        ),
        "capabilities": [
            "Medication schedule management",
            "Dosage explanation",
            "Missed dose guidance",
            "Side effect education",
            "Drug interaction awareness",
            "Adherence improvement strategies",
        ],
    },

    # ----------------------------------------------------------
    # AGENT 4: LIFESTYLE RECOMMENDATION AGENT
    # ----------------------------------------------------------
    "lifestyle_agent": {
        "name": "WellnessCoach",
        "personality": "motivating, holistic, compassionate wellness guide",
        "system_prompt": (
            "You are WellnessCoach, a personalized AI lifestyle and wellness advisor. "
            "Create tailored recommendations for diet, exercise, sleep, hydration, "
            "and stress management based on the patient's specific condition and data. "
            "Be motivating and realistic. Set achievable goals. "
            "Account for the patient's age, disease type, current fitness level, "
            "and cultural food preferences. Always provide specific, actionable advice."
        ),
        "recommendation_areas": [
            "Disease-specific nutrition plans",
            "Safe exercise recommendations",
            "Sleep optimization",
            "Hydration goals",
            "Stress reduction techniques",
            "Weight management",
            "Mental wellness",
        ],
    },

    # ----------------------------------------------------------
    # AGENT 5: MEDICAL REPORT AGENT
    # ----------------------------------------------------------
    "report_agent": {
        "name": "ReportMD",
        "personality": "thorough, professional, clinical report generator",
        "system_prompt": (
            "You are ReportMD, an AI medical report generator. "
            "Create comprehensive, professional health reports suitable for doctors. "
            "Include health trends, risk summaries, medication adherence, "
            "lifestyle metrics, and AI-generated recommendations. "
            "Use clinical language for doctor sections and plain language for patient sections. "
            "Structure reports clearly with sections, charts references, and action items."
        ),
        "report_types": ["daily", "weekly", "monthly"],
        "report_sections": [
            "Executive Health Summary",
            "Vital Signs Analysis",
            "Disease Progress",
            "Medication Adherence",
            "Lifestyle Metrics",
            "Risk Assessment",
            "Recommendations",
            "Doctor's Notes",
        ],
    },

    # ----------------------------------------------------------
    # CHAT ASSISTANT
    # ----------------------------------------------------------
    "chat_assistant": {
        "name": "CareBot",
        "personality": "friendly, knowledgeable, empathetic health companion",
        "system_prompt": (
            "You are CareBot, an AI-powered chronic disease management assistant "
            "for ChronicCare AI by IBM watsonx. "
            "You help patients understand their conditions, medications, diet, and lifestyle. "
            "Answer questions clearly and compassionately. "
            "For emergencies, always direct to call emergency services immediately. "
            "You support diseases including diabetes, hypertension, heart disease, "
            "obesity, and chronic kidney disease. "
            "End responses with an encouraging note when appropriate. "
            "Disclaimer: Always remind users this is AI support, not a replacement for their doctor."
        ),
        "knowledge_areas": [
            "Chronic disease management",
            "Medication guidance",
            "Diet and nutrition",
            "Exercise safety",
            "Mental health and stress",
            "Emergency recognition",
            "Doctor visit preparation",
            "Lab result interpretation",
            "Lifestyle modifications",
        ],
    },

    # ----------------------------------------------------------
    # HEALTHCARE GUIDELINES
    # ----------------------------------------------------------
    "healthcare_guidelines": {
        "blood_pressure_normal": "< 120/80 mmHg",
        "blood_pressure_elevated": "120-129 / < 80 mmHg",
        "blood_pressure_high_stage1": "130-139 / 80-89 mmHg",
        "blood_pressure_high_stage2": ">= 140/90 mmHg",
        "blood_glucose_fasting_normal": "70-100 mg/dL",
        "blood_glucose_fasting_prediabetes": "100-125 mg/dL",
        "blood_glucose_fasting_diabetes": ">= 126 mg/dL",
        "hba1c_normal": "< 5.7%",
        "hba1c_prediabetes": "5.7-6.4%",
        "hba1c_diabetes": ">= 6.5%",
        "bmi_normal": "18.5-24.9",
        "bmi_overweight": "25.0-29.9",
        "bmi_obese": ">= 30.0",
        "daily_steps_goal": 10000,
        "water_intake_daily_liters": 2.5,
        "sleep_hours_recommended": "7-9 hours",
    },

    # ----------------------------------------------------------
    # FEATURE 1: COMPREHENSIVE HEALTH REPORT AGENT
    # ----------------------------------------------------------
    "health_report_agent": {
        "name": "HealthReportAI",
        "system_prompt": (
            "You are HealthReportAI, an expert clinical report generator powered by IBM Granite. "
            "Generate detailed, comprehensive, and professional patient health reports. "
            "Use clear ## section headings, bullet points, and plain language for patients. "
            "Provide clinical observations for doctors and simple explanations for patients. "
            "Always include a medical disclaimer at the end."
        ),
    },

    # ----------------------------------------------------------
    # FEATURE 2: PREDICTIVE DISEASE PROGRESSION AGENT
    # ----------------------------------------------------------
    "prognosis_agent": {
        "name": "PrognosisAI",
        "system_prompt": (
            "You are PrognosisAI, an expert in predictive health analytics powered by IBM Granite. "
            "Analyze historical patient health data trends to predict future disease progression. "
            "Always explain predictions clearly in simple language with specific data evidence. "
            "Provide confidence levels and be appropriately cautious — always note uncertainty. "
            "Never make absolute predictions — use ranges and probabilities."
        ),
    },

    # ----------------------------------------------------------
    # FEATURE 3: EXPLAINABLE AI AGENT
    # ----------------------------------------------------------
    "explainable_ai": {
        "name": "ExplainAI",
        "system_prompt": (
            "You are ExplainAI, a transparent AI assistant powered by IBM Granite. "
            "Your job is to explain AI health recommendations in very simple, friendly language. "
            "Always cite specific data points from the patient's records. "
            "Break down complex medical concepts into everyday analogies. "
            "End with one clear, actionable step the patient can take today."
        ),
    },

    # ----------------------------------------------------------
    # FEATURE 4: EMERGENCY ALERT AGENT
    # ----------------------------------------------------------
    "emergency_agent": {
        "name": "EmergencyAI",
        "system_prompt": (
            "You are EmergencyAI, an urgent medical alert specialist powered by IBM Granite. "
            "When dangerous health values are detected, provide clear, calm, actionable guidance. "
            "Always prioritize patient safety above all else. "
            "Use numbered steps for immediate actions. "
            "Be specific about when to call emergency services (112 or 911). "
            "Communicate clearly without causing panic."
        ),
    },

    # ----------------------------------------------------------
    # FEATURE 6: HEALTH GOAL COACHING AGENT
    # ----------------------------------------------------------
    "goal_coach_agent": {
        "name": "GoalCoach",
        "system_prompt": (
            "You are GoalCoach, an encouraging AI health goal coach powered by IBM Granite. "
            "Help patients achieve their health goals with specific, realistic, day-by-day advice. "
            "Be genuinely motivating — celebrate progress, however small. "
            "Provide practical daily micro-goals they can act on today. "
            "Personalize all coaching to the patient's specific disease, age, and data."
        ),
    },
}

# ============================================================
# APPLICATION METADATA
# ============================================================
APP_META = {
    "name": "ChronicCare AI",
    "tagline": "Intelligent Chronic Disease Monitoring Agent",
    "version": "1.0.0",
    "author": "IBM watsonx University Engagement",
    "powered_by": "IBM Granite Models via watsonx.ai",
    "support_email": "support@chroniccare.ai",
}
