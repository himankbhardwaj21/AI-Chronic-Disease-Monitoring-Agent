"""
app.py — ChronicCare AI Development Entry Point
IBM watsonx.ai Powered Chronic Disease Monitoring Agent

Local development:  python app.py
Production (WSGI):  gunicorn wsgi:app
"""

import os
from dotenv import load_dotenv

load_dotenv()

from app_factory import create_app  # noqa: E402  (must be after load_dotenv)
from config import configure_logging  # noqa: E402

# Determine environment — default to development for direct python app.py runs
env = os.getenv("FLASK_ENV", "development")
app = create_app(env)
configure_logging(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    print("""
+----------------------------------------------------------+
|          ChronicCare AI  --  IBM watsonx.ai             |
|    Intelligent Chronic Disease Monitoring Agent         |
+----------------------------------------------------------+
|  Server  : http://127.0.0.1:{port}
|  AI Model: IBM Granite via watsonx.ai
|  Mode    : {env}
+----------------------------------------------------------+
""".format(port=port, env=env.upper()))

    app.run(host="0.0.0.0", port=port, debug=debug)
