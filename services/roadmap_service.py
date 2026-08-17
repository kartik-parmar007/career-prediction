"""
Roadmap Service: Synthesizes user assessment context, weak topics, and static curriculum data.
"""

from utils.json_loader import get_career_by_id, get_skills_data, get_roadmaps_data
from services.llm_service import generate_personalized_roadmap_llm

def create_user_roadmap(payload):
    """
    Assembles rich context from user payload and invokes LLM/Demo roadmap generator.
    
    Expected payload fields:
        - career_id: str (e.g. "fullstack")
        - compatibility_pct: int (e.g. 87)
        - readiness_pct: int (e.g. 70)
        - weak_topics: list of strings
        - strong_topics: list of strings
        - weekly_hours: str
    """
    career_id = payload.get("career_id", "fullstack")
    career_info = get_career_by_id(career_id)
    skills_data = get_skills_data().get(career_id, {})
    roadmaps_data = get_roadmaps_data().get(career_id, {})

    career_title = career_info.get("title", "IT Specialist") if career_info else "Software Developer"

    readiness = int(payload.get("readiness_pct", 70))
    if readiness >= 80:
        current_level = "Intermediate / Advanced"
    elif readiness >= 60:
        current_level = "Beginner+"
    else:
        current_level = "Beginner Foundations"

    context_data = {
        "career_id": career_id,
        "career_title": career_title,
        "compatibility_pct": int(payload.get("compatibility_pct", 85)),
        "readiness_pct": readiness,
        "current_level": current_level,
        "weak_topics": payload.get("weak_topics", []),
        "strong_topics": payload.get("strong_topics", []),
        "weekly_hours": payload.get("weekly_hours", "10 - 15 hours/week"),
        "standard_curriculum": {
            "skills": skills_data,
            "base_phases": roadmaps_data.get("phases", [])
        }
    }

    roadmap_result = generate_personalized_roadmap_llm(context_data)
    return roadmap_result
