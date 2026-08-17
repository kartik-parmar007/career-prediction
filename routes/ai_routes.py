"""
AI Routes: Endpoints for AI Roadmap Generation and Career Mentor Chatbot.
"""

from flask import Blueprint, request, jsonify
from services.roadmap_service import create_user_roadmap
from services.llm_service import generate_mentor_chat_response

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.route("/api/ai/roadmap", methods=["POST"])
def generate_roadmap():
    """
    POST /api/ai/roadmap
    Generates a 6-phase tailored roadmap based on user's assessment and technical readiness results.
    """
    data = request.get_json() or {}
    try:
        roadmap = create_user_roadmap(data)
        return jsonify({"status": "success", "roadmap": roadmap})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to generate roadmap: {str(e)}"}), 500

@ai_bp.route("/api/ai/chat", methods=["POST"])
def mentor_chat():
    """
    POST /api/ai/chat
    Responds to user questions in the AI Career Mentor interface.
    """
    data = request.get_json() or {}
    messages = data.get("messages", [])
    session_context = data.get("session_context", {})

    if not messages:
        return jsonify({"status": "error", "message": "No messages provided"}), 400

    try:
        reply_data = generate_mentor_chat_response(messages, session_context)
        return jsonify({
            "status": "success",
            "message": {
                "role": "assistant",
                "content": reply_data["response"]
            },
            "mode": reply_data.get("mode", "demo_mode"),
            "model": reply_data.get("model", "AI Mentor")
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Mentor chat error: {str(e)}"}), 500
