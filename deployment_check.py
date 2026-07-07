"""
deployment_check.py — ChronicCare AI Deployment Readiness Validator
Checks imports, secrets, routes, templates, and dependencies.
Run: python deployment_check.py
"""
import os, sys, importlib, pathlib

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"
results = []

def check(label, ok, detail="", level="pass"):
    tag = PASS if ok else (WARN if level == "warn" else FAIL)
    results.append((ok, level, label, detail))
    print(f"{tag} {label}" + (f"  ({detail})" if detail else ""))
    return ok

print("=" * 60)
print(" ChronicCare AI — Deployment Readiness Check")
print("=" * 60)
print()

# ── 1. PYTHON IMPORTS ──────────────────────────────────────
print("[ 1/7 ] DEPENDENCY IMPORTS")
deps = {
    "flask":           "Flask",
    "flask_sqlalchemy":"Flask-SQLAlchemy",
    "flask_wtf":       "Flask-WTF",
    "dotenv":          "python-dotenv",
    "sqlalchemy":      "SQLAlchemy",
    "wtforms":         "WTForms",
    "requests":        "requests",
    "dateutil":        "python-dateutil",
    "reportlab":       "reportlab",
    "PIL":             "Pillow",
    "gunicorn":        "gunicorn",
    "email_validator": "email-validator",
    "ibm_watsonx_ai":  "ibm-watsonx-ai",
}
for mod, pkg in deps.items():
    try:
        importlib.import_module(mod)
        check(f"  {pkg}", True)
    except ImportError as e:
        check(f"  {pkg}", False, str(e))

print()

# ── 2. PROJECT FILE EXISTENCE ──────────────────────────────
print("[ 2/7 ] PROJECT FILES")
required_files = [
    ("app.py",          "Application entry point"),
    ("wsgi.py",         "Production WSGI entry point"),
    ("app_factory.py",  "Flask factory"),
    ("config.py",       "Configuration"),
    ("requirements.txt","Dependencies"),
    ("Procfile",        "Render/Heroku start command"),
    ("render.yaml",     "Render deployment config"),
    ("runtime.txt",     "Python version"),
    ("Dockerfile",      "Docker container definition"),
    ("LICENSE",         "MIT License"),
    (".env.example",    "Environment template"),
    ("README.md",       "Documentation"),
]
for f, desc in required_files:
    exists = os.path.isfile(f)
    check(f"  {f}", exists, desc)

print()

# ── 3. SECRET / CREDENTIAL CHECK ──────────────────────────
print("[ 3/7 ] SECRET SECURITY CHECK")
import re

# Scan .py files for hardcoded-looking secrets
def scan_for_secrets(path):
    issues = []
    patterns = [
        (r'(api_key|apikey|API_KEY)\s*=\s*["\'][a-zA-Z0-9_\-]{20,}["\']', "Possible hardcoded API key"),
        (r'(password|passwd|secret)\s*=\s*["\'][^"\']{8,}["\']', "Possible hardcoded password"),
    ]
    try:
        text = open(path, encoding="utf-8").read()
        for pattern, label in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Check it's NOT inside os.getenv or a comment
                matches = re.findall(pattern, text, re.IGNORECASE)
                issues.append(f"{path}: {label}")
    except Exception:
        pass
    return issues

secret_issues = []
for f in pathlib.Path(".").rglob("*.py"):
    if "__pycache__" in str(f):
        continue
    secret_issues.extend(scan_for_secrets(str(f)))

check("  No hardcoded secrets in .py files", len(secret_issues) == 0,
      f"{len(secret_issues)} potential issue(s)" if secret_issues else "")
for issue in secret_issues[:3]:
    print(f"    {WARN} {issue}")

# Check .env is not committed
gitignore_ok = False
if os.path.isfile(".gitignore"):
    content = open(".gitignore").read()
    gitignore_ok = ".env" in content
check("  .env in .gitignore", gitignore_ok)

# Check .env.example has no real-looking keys
# Exclude obvious placeholders: strings containing "your_", "_here", "example", "change", "placeholder"
if os.path.isfile(".env.example"):
    env_ex = open(".env.example").read()
    real_key_match = re.search(r'IBM_API_KEY=([a-zA-Z0-9_\-]{20,})', env_ex)
    if real_key_match:
        candidate = real_key_match.group(1)
        placeholder_markers = ["your_", "_here", "example", "change", "placeholder", "test", "xxx"]
        is_placeholder = any(m in candidate.lower() for m in placeholder_markers)
        no_real_keys = is_placeholder
    else:
        no_real_keys = True
    check("  .env.example has only placeholder values", no_real_keys)

print()

# ── 4. FLASK APP BOOT ──────────────────────────────────────
print("[ 4/7 ] FLASK APPLICATION BOOT")
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("SECRET_KEY", "test-deploy-check")
os.environ["IBM_API_KEY"] = ""      # Force demo mode
os.environ["IBM_PROJECT_ID"] = ""

try:
    from app_factory import create_app, db
    app = create_app("development")
    check("  Flask app created", True)

    with app.app_context():
        from models.patient import Patient
        from models.health_record import HealthRecord
        from models.medication import Medication
        from models.alert import Alert
        from models.health_timeline import HealthTimeline
        from models.health_goal import HealthGoal
        check("  All 6 models imported", True)

        pc = Patient.query.count()
        check("  Database accessible", True, f"{pc} patient(s)")

except Exception as e:
    check("  Flask app boot", False, str(e))
    print(f"\n  ERROR: {e}")

print()

# ── 5. ROUTE VALIDATION ────────────────────────────────────
print("[ 5/7 ] ROUTE VALIDATION")
ROUTES = [
    ("/",                   "Root redirect"),
    ("/dashboard/1",        "Dashboard"),
    ("/patients/",          "Patient list"),
    ("/patients/1",         "Patient view"),
    ("/health/input/1",     "Health data input"),
    ("/health/history/1",   "Health history"),
    ("/agents/1",           "AI Agents hub"),
    ("/agents/1/vitals",    "VitalGuard"),
    ("/agents/1/risk",      "RiskSense AI"),
    ("/agents/1/medication","MedCoach"),
    ("/agents/1/lifestyle", "WellnessCoach"),
    ("/agents/1/report",    "ReportMD"),
    ("/chat/1",             "CareBot chat"),
    ("/reports/1",          "Reports"),
    ("/health-report/1",    "AI Health Report"),
    ("/prediction/1",       "AI Prediction"),
    ("/emergency/1",        "Emergency Alerts"),
    ("/timeline/1",         "Health Timeline"),
    ("/goals/1",            "Health Goals"),
    ("/health/api/chart/1", "Chart data API"),
    ("/health/api/stats/1", "Stats API"),
]
route_fails = 0
with app.test_client() as c:
    for path, label in ROUTES:
        rv = c.get(path)
        ok = rv.status_code in (200, 302)
        if not ok:
            route_fails += 1
        check(f"  {label} ({path})", ok, str(rv.status_code))

print()

# ── 6. TEMPLATE FILES ──────────────────────────────────────
print("[ 6/7 ] TEMPLATE FILES")
template_files = [
    "templates/base.html",
    "templates/dashboard.html",
    "templates/partials/sidebar_content.html",
    "templates/agents/agents_home.html",
    "templates/agents/vitals_analysis.html",
    "templates/agents/risk_prediction.html",
    "templates/agents/medication_guidance.html",
    "templates/agents/lifestyle_recommendations.html",
    "templates/agents/report_agent.html",
    "templates/chat/chat.html",
    "templates/patients/form.html",
    "templates/patients/list.html",
    "templates/patients/view.html",
    "templates/health_data/input.html",
    "templates/health_data/history.html",
    "templates/reports/reports.html",
    "templates/features/health_report.html",
    "templates/features/prediction.html",
    "templates/features/emergency.html",
    "templates/features/timeline.html",
    "templates/features/goals.html",
]
for tf in template_files:
    check(f"  {tf}", os.path.isfile(tf))

static_files = [
    "static/css/style.css",
    "static/css/enhanced.css",
    "static/js/main.js",
    "static/js/dashboard.js",
]
for sf in static_files:
    check(f"  {sf}", os.path.isfile(sf))

print()

# ── 7. PRODUCTION CONFIG ───────────────────────────────────
print("[ 7/7 ] PRODUCTION CONFIG CHECK")
proc = open("Procfile").read().strip() if os.path.isfile("Procfile") else ""
check("  Procfile uses wsgi:app", "wsgi:app" in proc, proc[:60])
check("  Procfile uses gunicorn", "gunicorn" in proc)

rt = open("runtime.txt").read().strip() if os.path.isfile("runtime.txt") else ""
check("  runtime.txt specifies Python 3.11", "3.11" in rt, rt)

env_example = open(".env.example").read() if os.path.isfile(".env.example") else ""
check("  .env.example has IBM_API_KEY placeholder", "IBM_API_KEY=" in env_example)
check("  .env.example has IBM_PROJECT_ID placeholder", "IBM_PROJECT_ID=" in env_example)
check("  .env.example has SECRET_KEY", "SECRET_KEY=" in env_example)

from config import configure_logging, config_map
check("  configure_logging() function exists", callable(configure_logging))
check("  production config class exists", "production" in config_map)
prod_cfg = config_map["production"]
check("  DEBUG=False in production", prod_cfg.DEBUG == False)
check("  SESSION_COOKIE_SECURE in production", prod_cfg.SESSION_COOKIE_SECURE == True)

print()
print("=" * 60)

# SUMMARY
total = len(results)
passed = sum(1 for ok, _, _, _ in results if ok)
failed = sum(1 for ok, lv, _, _ in results if not ok and lv != "warn")

print(f" SUMMARY: {passed}/{total} checks passed | {failed} failures")
print("=" * 60)
if failed == 0:
    print(" STATUS: DEPLOYMENT READY")
    print("   GitHub Ready  : YES")
    print("   Render Ready  : YES")
    print("   Production    : YES")
else:
    print(f" STATUS: {failed} issue(s) must be fixed before deployment")
    print()
    for ok, lv, label, detail in results:
        if not ok:
            print(f"  FIX: {label}" + (f" — {detail}" if detail else ""))
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
