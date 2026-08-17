"""
Career Routes: Endpoints for Career Catalog, 15-Question Assessment, and ML Career Prediction.
"""

from flask import Blueprint, request, jsonify
from utils.json_loader import get_all_careers, get_career_by_id, get_career_questions
from services.ml_service import get_career_recommendations

career_bp = Blueprint("career_bp", __name__)

@career_bp.route("/api/careers", methods=["GET"])
def list_careers():
    """Returns list of all 12 IT career categories."""
    try:
        careers = get_all_careers()
        return jsonify({"status": "success", "careers": careers})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@career_bp.route("/api/careers/<career_id>", methods=["GET"])
def get_career(career_id):
    """Returns details for a single career."""
    career = get_career_by_id(career_id)
    if not career:
        return jsonify({"status": "error", "message": "Career not found"}), 404
    return jsonify({"status": "success", "career": career})

@career_bp.route("/api/career-questions", methods=["GET"])
def list_career_questions():
    """Returns the exactly 15 career assessment questions."""
    try:
        questions = get_career_questions()
        return jsonify({"status": "success", "questions": questions, "total": len(questions)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@career_bp.route("/api/career/predict", methods=["POST"])
def predict_career():
    """
    Evaluates 15 answers and returns ML Top 3 Recommendations + full matches.
    """
    data = request.get_json() or {}
    answers = data.get("answers", {})

    if not answers:
        return jsonify({"status": "error", "message": "Missing assessment answers"}), 400

    try:
        top_recs, all_compat = get_career_recommendations(answers, top_k=3)

        # Enrich recommendations with full career details
        enriched_recs = []
        for rec in top_recs:
            cid = rec["career_id"]
            details = get_career_by_id(cid) or {}
            enriched_recs.append({
                "career_id": cid,
                "rank": rec["rank"],
                "compatibility": rec["compatibility"],
                "title": details.get("title", cid),
                "icon": details.get("icon", "fa-solid fa-laptop-code"),
                "badge": details.get("badge", "Recommended"),
                "short_description": details.get("short_description", ""),
                "description": details.get("description", ""),
                "difficulty": details.get("difficulty", "Moderate"),
                "salary_range": details.get("salary_range", "$80k - $140k"),
                "key_skills": details.get("key_skills", []),
                "typical_roles": details.get("typical_roles", []),
                "why_matches": details.get("why_matches", "Strong alignment with your problem-solving style."),
                "recommended_next_step": details.get("recommended_next_step", f"Take the {details.get('title', cid)} skill test.")
            })

        return jsonify({
            "status": "success",
            "top_recommendations": enriched_recs,
            "all_compatibilities": all_compat
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Prediction failed: {str(e)}"}), 500
