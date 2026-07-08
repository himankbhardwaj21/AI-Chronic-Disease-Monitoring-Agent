<div align="center">

# ChronicCare AI

### Intelligent Chronic Disease Monitoring Agent

**Powered by IBM Granite Models via IBM watsonx.ai**

[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![IBM watsonx](https://img.shields.io/badge/IBM-watsonx.ai-054ADA?style=flat&logo=ibm&logoColor=white)](https://www.ibm.com/watsonx)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat)](LICENSE)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=flat&logo=render&logoColor=white)](https://render.com)

*Enterprise-grade AI healthcare application | IBM University Engagement Showcase*

</div>

---

## Problem Statement

Chronic diseases — including Diabetes, Hypertension, Heart Disease, Obesity, and Chronic Kidney Disease — affect over **500 million people worldwide**. Managing these conditions requires continuous health monitoring, medication adherence, lifestyle adjustments, and timely medical intervention.

**The challenge:** Most patients lack intelligent, real-time tools that can:
- Continuously analyze their health data and detect anomalies early
- Predict disease progression before a crisis occurs
- Provide personalized, evidence-based lifestyle guidance
- Generate actionable medical reports for healthcare providers
- Respond to emergencies with immediate, clear guidance

**ChronicCare AI** solves this by combining IBM Granite's enterprise AI capabilities with a purpose-built multi-agent healthcare monitoring system — putting an intelligent health companion in every patient's hands.

---

## Features

### Core AI Agents (IBM Granite)

| Agent | Name | Capability |
|-------|------|------------|
| Health Monitoring | **VitalGuard** | Real-time vital sign analysis, abnormality detection, daily health scoring |
| Risk Prediction | **RiskSense AI** | Disease progression prediction, risk scoring (Low/Medium/High/Critical) |
| Medication Coach | **MedCoach** | Adherence tracking, dosage guidance, missed dose protocols |
| Lifestyle Guide | **WellnessCoach** | Personalized diet, exercise, sleep, and stress management plans |
| Report Generator | **ReportMD** | Daily/Weekly/Monthly professional health reports with PDF export |
| Chat Assistant | **CareBot** | Conversational AI health companion with voice I/O |

### Extended AI Features

| Feature | Description |
|---------|-------------|
| **AI Health Report** | 18-section comprehensive health analysis report, downloadable as PDF |
| **Predictive Progression** | 7 / 30 / 90-day disease progression forecasts with confidence levels |
| **Explainable AI** | "Why this recommendation?" — transparent AI reasoning in plain language |
| **Emergency Alerts** | Real-time monitoring with color-coded severity (Green → Critical), AI explanation |
| **Health Timeline** | Chronological event log — auto-generated from every health data entry |
| **Health Goals** | AI-coached goal tracking with progress rings, badges, and daily micro-goals |

### Application Features

- **Multi-patient profiles** — manage multiple patients simultaneously
- **Health data logging** — vitals, lifestyle metrics, mood, symptoms, notes
- **Comprehensive dashboard** — risk meter, health score ring, 6 live charts
- **Medication adherence tracker** — visual adherence scoring per medication
- **PDF report download** — professional reports via ReportLab
- **Dark / Light mode** — persistent preference via localStorage
- **Voice input & output** — browser Web Speech API integration
- **Floating AI assistant button** — instant access to CareBot from any page
- **Skeleton loading screens** — polished loading UX during AI generation
- **Mobile responsive** — Bootstrap 5 with offcanvas sidebar
- **Demo mode** — runs fully without IBM credentials (displays sample AI responses)

---

## Screenshots

> **Dashboard** — Patient vitals, risk meter, health score, Chart.js visualizations
<img width="959" height="539" alt="3i" src="https://github.com/user-attachments/assets/b279afd3-7d59-4acd-95ed-a531248713e3" />


> **AI Health Report** — 18-section IBM Granite generated clinical report
<img width="959" height="539" alt="10i" src="https://github.com/user-attachments/assets/801fa905-2c54-4eaa-ac24-650de8520dce" />


> **Predictive Progression** — 7/30/90-day disease forecast with risk donut
<img width="959" height="539" alt="28i" src="https://github.com/user-attachments/assets/c5ed72c7-516d-4c7a-ade2-1cdd9bf44ce7" />


> **Emergency Alerts** — Color-coded real-time alert dashboard
<img width="959" height="539" alt="15i" src="https://github.com/user-attachments/assets/2705c2a4-48d1-4aa9-ab3f-33bfc0dcc1b0" />


> **Health Timeline** — Chronological health event cards
<img width="959" height="539" alt="16i" src="https://github.com/user-attachments/assets/204f24f4-3e84-48ba-8a07-26bce44000a7" />


> **Health Goals** — Progress rings, AI coaching, achievement badges
<img width="959" height="539" alt="18i" src="https://github.com/user-attachments/assets/55403f6f-1361-471b-8f39-c5d1526d46ab" />


> **CareBot Chat** — Conversational IBM Granite health assistant
<img width="959" height="539" alt="6i" src="https://github.com/user-attachments/assets/35569697-ab4d-4c1c-929e-905f15a20a97" />


---

## Technology Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Web Framework | Python Flask 3.1 |
| ORM / Database | SQLAlchemy 2.0 + SQLite (dev) / PostgreSQL (prod) |
| AI / LLM | IBM Granite via IBM watsonx.ai |
| PDF Generation | ReportLab 5.0 |
| Production Server | Gunicorn 26.0 |
| Environment | python-dotenv |

### Frontend
| Component | Technology |
|-----------|-----------|
| UI Framework | Bootstrap 5.3 |
| Templating | Jinja2 (Flask) |
| Charts | Chart.js 4.4 |
| Icons | Bootstrap Icons 1.11 |
| Fonts | Inter (Google Fonts) |
| Voice | Web Speech API (browser-native) |

---

## IBM watsonx.ai Integration

ChronicCare AI uses IBM Granite models via the **IBM watsonx.ai REST API** for all AI generation:

### Authentication Flow
```
Patient Data → Prompt Builder → IBM IAM Token Auth → Granite REST API → Response Parser → UI
```

### IBM Granite Model
```
Model ID:  ibm/granite-3-8b-instruct
Endpoint:  https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29
Auth:      IBM Cloud API Key → IAM Bearer Token (auto-refreshed every ~55 minutes)
```

### Agent Prompt Customization
All AI agent prompts are centrally configured in [`config.py`](config.py) under `AGENT_INSTRUCTIONS`:

```python
AGENT_INSTRUCTIONS = {
    "health_monitoring_agent": {
        "system_prompt": "You are VitalGuard...",  # Customize here
    },
    "risk_prediction_agent": {
        "system_prompt": "You are RiskSense AI...",
    },
    # ... 8 more agents
}
```

---

## Project Architecture

```
ChronicCare AI/
│
├── app.py                  # Development entry point
├── wsgi.py                 # Production WSGI entry point (Gunicorn)
├── app_factory.py          # Flask application factory + DB init + seeding
├── config.py               # All config + AGENT_INSTRUCTIONS + logging
├── requirements.txt
├── Procfile                # Render / Heroku deployment
├── render.yaml             # Render.com auto-deploy config
├── runtime.txt             # Python version pin
├── .env.example            # Credential template (commit this)
│
├── routes/                 # Flask blueprints (one per feature)
│   ├── dashboard.py        # Main dashboard + AI insights API
│   ├── patients.py         # Patient CRUD + medication management
│   ├── health_data.py      # Vitals input + timeline auto-generation
│   ├── agents.py           # 5 AI agent pages + AJAX endpoints
│   ├── chat.py             # CareBot multi-turn chat
│   ├── reports.py          # Report pages + PDF download
│   ├── health_report.py    # Feature 1: Comprehensive AI report
│   ├── prediction.py       # Feature 2: Disease progression prediction
│   ├── explain.py          # Feature 3: Explainable AI API
│   ├── emergency.py        # Feature 4: Emergency alert system
│   ├── timeline.py         # Feature 5: Health timeline
│   └── goals.py            # Feature 6: Smart health goals
│
├── services/               # Business logic layer
│   ├── watsonx_service.py  # IBM Granite API client (IAM auth + generation)
│   ├── agent_service.py    # 5 core AI agents
│   ├── extended_agent_service.py  # 5 extended AI agents (Features 1-6)
│   ├── health_service.py   # Health record analytics + chart data
│   ├── timeline_service.py # Timeline event generation
│   └── report_service.py   # PDF report generation (ReportLab)
│
├── models/                 # SQLAlchemy ORM models
│   ├── patient.py          # Patient profile
│   ├── health_record.py    # Vital signs + lifestyle metrics
│   ├── medication.py       # Medication tracking + adherence
│   ├── alert.py            # AI-generated health alerts
│   ├── health_timeline.py  # Chronological health events
│   └── health_goal.py      # Patient health goals + progress
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout (sidebar, dark mode, FAB)
│   ├── dashboard.html      # Main dashboard
│   ├── partials/           # Reusable sidebar component
│   ├── agents/             # 5 AI agent pages
│   ├── features/           # 6 extended feature pages
│   ├── patients/           # Patient management pages
│   ├── health_data/        # Data input + history
│   ├── chat/               # CareBot chat interface
│   └── reports/            # Reports page
│
├── static/
│   ├── css/
│   │   ├── style.css       # Core styles (glassmorphism, dark mode)
│   │   └── enhanced.css    # Feature enhancements (animations, rings)
│   └── js/
│       ├── main.js         # Dark mode, toast, BMI colors, utilities
│       └── dashboard.js    # Chart.js visualizations
│
└── utils/
    ├── helpers.py          # BMI, age, risk color utilities
    ├── validators.py       # Form input validation
    └── formatters.py       # AI response → HTML formatter
```

---

## Installation Guide

### Prerequisites
- Python **3.11+**
- `pip` package manager
- IBM Cloud account (free tier works)
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/chroniccare-ai.git
cd chroniccare-ai
```

### Step 2 — Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate — macOS/Linux
source venv/bin/activate

# Activate — Windows
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

```bash
# Copy the template
cp .env.example .env

# Open .env and fill in your credentials
```

### Step 5 — Run the Application

```bash
python app.py
```

Open **http://127.0.0.1:5000** — the app auto-creates the database and seeds a demo patient.

---

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `IBM_API_KEY` | **Yes** | IBM Cloud API Key | `jy13yTgY0...` |
| `IBM_PROJECT_ID` | **Yes** | watsonx.ai Project ID | `9db8348a-2bdb-...` |
| `WATSONX_URL` | **Yes** | Inference endpoint | `https://us-south.ml.cloud.ibm.com` |
| `GRANITE_MODEL_ID` | No | Granite model to use | `ibm/granite-3-8b-instruct` |
| `SECRET_KEY` | **Yes** | Flask session secret | `your-random-secret-key` |
| `FLASK_ENV` | No | App environment | `development` or `production` |
| `DATABASE_URL` | No | Database URL | `sqlite:///data/chroniccare.db` |
| `MAX_TOKENS` | No | Max AI response tokens | `1024` |
| `TEMPERATURE` | No | AI creativity (0.0-1.0) | `0.7` |

### Getting IBM Credentials

1. Sign up at [IBM Cloud](https://cloud.ibm.com) (free tier available)
2. Create a **watsonx.ai** instance at [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
3. Create a new **Project** and copy the **Project ID**
4. Go to **Manage → Access (IAM) → API Keys** → Create an API Key
5. Add both to your `.env` file

### Generating a Secure SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Running Locally

### Development Server
```bash
python app.py
# → http://127.0.0.1:5000
```

### Production Server (local test)
```bash
# Set production environment
export FLASK_ENV=production   # Linux/macOS
set FLASK_ENV=production      # Windows

# Start with Gunicorn
gunicorn wsgi:app --workers 2 --bind 0.0.0.0:5000 --timeout 120
```

### Demo Mode (no IBM credentials needed)
The app runs in **demo mode** without IBM credentials — all AI features show realistic sample responses. Full AI activates automatically once credentials are added to `.env`.

---

## Deployment Instructions

### Option 1 — Render.com (Recommended)

Render provides **free-tier hosting** with automatic deployments from GitHub.

#### Step-by-step:

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit — ChronicCare AI"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/chroniccare-ai.git
   git push -u origin main
   ```

2. **Create Render service:**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click **New → Web Service**
   - Connect your GitHub repository
   - Render auto-detects `render.yaml` and `Procfile`

3. **Set environment variables** in Render dashboard → Environment tab:
   ```
   IBM_API_KEY        = your_api_key
   IBM_PROJECT_ID     = your_project_id
   FLASK_ENV          = production
   SESSION_COOKIE_SECURE = True
   ```
   *(SECRET_KEY is auto-generated by Render)*

4. Click **Deploy** — your app will be live at `https://chroniccare-ai.onrender.com`

### Option 2 — Railway.app

```bash
# Install Railway CLI
npm install -g @railway/cli

railway login
railway init
railway up

# Set environment variables
railway variables set IBM_API_KEY=your_key
railway variables set IBM_PROJECT_ID=your_id
railway variables set FLASK_ENV=production
```

### Option 3 — IBM Cloud Code Engine

```bash
# Install IBM Cloud CLI
ibmcloud login

# Create Code Engine project
ibmcloud ce project create --name chroniccare

# Deploy
ibmcloud ce application create \
  --name chroniccare-ai \
  --image icr.io/your-namespace/chroniccare-ai:latest \
  --port 5000 \
  --env FLASK_ENV=production \
  --env IBM_API_KEY=your_key \
  --env IBM_PROJECT_ID=your_id
```

### Option 4 — Docker

```dockerfile
# Build
docker build -t chroniccare-ai .

# Run
docker run -p 5000:5000 \
  -e IBM_API_KEY=your_key \
  -e IBM_PROJECT_ID=your_id \
  -e SECRET_KEY=your_secret \
  -e FLASK_ENV=production \
  chroniccare-ai
```

> **Note:** A `Dockerfile` is not included by default — create one based on `python:3.11-slim`.

### Production Checklist

Before going live, ensure:
- [ ] `SECRET_KEY` is a strong random value (not the default)
- [ ] `FLASK_ENV=production` and `FLASK_DEBUG=False`
- [ ] `SESSION_COOKIE_SECURE=True` (HTTPS required)
- [ ] IBM credentials set as environment variables (not in `.env` on server)
- [ ] `.env` is in `.gitignore` (it is — already configured)
- [ ] Database is backed up regularly

---

## Future Scope

| Feature | Description |
|---------|-------------|
| PostgreSQL | Production database for multi-tenant deployment |
| User Authentication | Flask-Login / JWT for multi-user access |
| Real-time Monitoring | WebSocket integration for live vital sign streaming |
| Wearable Integration | Fitbit, Apple Health, Google Fit API connectors |
| Multi-language Support | IBM Granite multilingual model for 10+ languages |
| Push Notifications | Browser push / email alerts for emergency conditions |
| Family Monitoring | Caregiver accounts linked to patient profiles |
| Telemedicine Integration | Video consultation booking via healthcare APIs |
| FHIR Compliance | HL7 FHIR standard for EHR system integration |
| Mobile App | React Native wrapper for iOS / Android |
| HbA1c Predictor | ML model for long-term glucose control forecasting |
| Clinical Decision Support | ICD-10 code suggestions for clinical documentation |

---

## License

```
MIT License

Copyright (c) 2025 ChronicCare AI — IBM watsonx University Engagement

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Disclaimer

ChronicCare AI is an educational and demonstration application built for the **IBM watsonx University Engagement Programme**. It is powered by IBM Granite AI models for research and showcase purposes.

**This application does NOT provide medical advice.** All AI-generated content is for informational purposes only and must not replace consultation with a licensed healthcare professional. Always consult your doctor for medical decisions.

---

<div align="center">

**Built with IBM Granite AI via watsonx.ai**

IBM University Engagement | Chronic Disease Management | AI Healthcare Research

</div>
