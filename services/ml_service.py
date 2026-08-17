"""
ML Service: Encapsulates ML inference and questionnaire result formatting.
"""

import sys
import os

# Add ml folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml"))

try:
    from predict import predict_career_matches
except ImportError:
    predict_career_matches = None

def get_career_recommendations(answers_dict, top_k=3):
    """
    Evaluates questionnaire answers and returns ranked career recommendations.
    Provides graceful fallback if the ML model is not yet compiled.
    """
    if predict_career_matches is not None:
        try:
            recommendations, all_compatibilities = predict_career_matches(answers_dict, top_k=top_k)
            return recommendations, all_compatibilities
        except Exception as e:
            print(f"[ML Service Warning] Inference error: {e}. Falling back to rule-based scoring.")

    # Rule-based fallback calculation
    return rule_based_career_scoring(answers_dict, top_k=top_k)

def rule_based_career_scoring(answers, top_k=3):
    """
    Heuristic rule-based fallback scoring in case ML model is unavailable.
    """
    scores = {
        "frontend": 50,
        "backend": 50,
        "fullstack": 50,
        "mobile": 50,
        "data_analyst": 50,
        "data_scientist": 50,
        "ai_ml": 50,
        "devops_cloud": 50,
        "cybersecurity": 50,
        "qa_automation": 50,
        "ui_ux": 50,
        "data_engineer": 50
    }

    ui_val = float(answers.get("ui_design_enjoyment", 3))
    prog_val = float(answers.get("programming_enjoyment", 3))
    math_val = float(answers.get("math_enjoyment", 3))
    stats_val = float(answers.get("statistics_comfort", 3))
    data_val = float(answers.get("data_preference", 3))
    cloud_val = float(answers.get("cloud_infra_enjoyment", 3))
    sec_val = float(answers.get("cybersecurity_enjoyment", 3))
    debug_val = float(answers.get("debugging_enjoyment", 3))
    archetype = answers.get("career_archetype", "")

    # Apply weighted heuristics
    scores["ui_ux"] += ui_val * 7 - prog_val * 2
    scores["frontend"] += ui_val * 5 + prog_val * 4
    scores["backend"] += prog_val * 5 + debug_val * 3 - ui_val * 2
    scores["fullstack"] += prog_val * 4 + ui_val * 3 + debug_val * 2
    scores["mobile"] += prog_val * 4 + ui_val * 3
    scores["data_analyst"] += data_val * 6 + stats_val * 4
    scores["data_scientist"] += math_val * 5 + stats_val * 5 + data_val * 4
    scores["ai_ml"] += math_val * 5 + prog_val * 4 + data_val * 4
    scores["devops_cloud"] += cloud_val * 7 + debug_val * 3
    scores["cybersecurity"] += sec_val * 8 + debug_val * 2
    scores["qa_automation"] += debug_val * 7 + prog_val * 2
    scores["data_engineer"] += data_val * 5 + cloud_val * 4 + prog_val * 3

    if archetype == "creative_visual":
        scores["ui_ux"] += 15
        scores["frontend"] += 10
    elif archetype == "analytical_data":
        scores["data_scientist"] += 12
        scores["data_analyst"] += 12
        scores["ai_ml"] += 10
    elif archetype == "systems_security":
        scores["devops_cloud"] += 12
        scores["cybersecurity"] += 14

    sorted_careers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    all_compat = {}
    recs = []

    for rank, (cid, raw_score) in enumerate(sorted_careers, start=1):
        if rank == 1:
            compat = 88
        elif rank == 2:
            compat = 82
        elif rank == 3:
            compat = 76
        else:
            compat = max(45, min(70, int(raw_score * 0.7)))

        all_compat[cid] = compat
        if rank <= top_k:
            recs.append({
                "career_id": cid,
                "compatibility": compat,
                "rank": rank
            })

    return recs, all_compat
