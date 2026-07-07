"""
routes/chat.py — AI Chat Assistant (CareBot)
"""

from flask import Blueprint, render_template, request, jsonify, session
from models.patient import Patient
from services.agent_service import AgentService

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/<int:patient_id>")
def chat_home(patient_id: int):
    """Chat assistant page."""
    patient = Patient.query.get_or_404(patient_id)
    all_patients = Patient.query.filter_by(is_active=True).all()
    # Clear previous session history when loading new chat
    session_key = f"chat_history_{patient_id}"
    if session_key not in session:
        session[session_key] = []
    history = session[session_key]
    return render_template(
        "chat/chat.html",
        patient=patient,
        all_patients=all_patients,
        history=history,
        active_page="chat",
    )


@chat_bp.route("/api/<int:patient_id>/send", methods=["POST"])
def send_message(patient_id: int):
    """AJAX: process chat message and return AI response."""
    patient = Patient.query.get_or_404(patient_id)
    data = request.json or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    if len(user_message) > 2000:
        return jsonify({"error": "Message too long (max 2000 characters)"}), 400

    session_key = f"chat_history_{patient_id}"
    history = session.get(session_key, [])

    # Keep only last 10 turns to manage context
    if len(history) > 20:
        history = history[-20:]

    # Get AI response
    response = AgentService.chat_response(patient.to_dict(), history, user_message)

    # Update session history
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": response})
    session[session_key] = history
    session.modified = True

    return jsonify({
        "response": response,
        "patient_name": patient.name,
    })


@chat_bp.route("/api/<int:patient_id>/clear", methods=["POST"])
def clear_history(patient_id: int):
    """Clear chat history for a patient."""
    session_key = f"chat_history_{patient_id}"
    session[session_key] = []
    session.modified = True
    return jsonify({"status": "ok"})
