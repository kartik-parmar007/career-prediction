"""
Automated tests for Career Assessment and ML Prediction pipeline.
"""

import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.json_loader import get_all_careers, get_career_questions, get_career_by_id
from services.ml_service import get_career_recommendations

def test_careers_catalog_structure():
    careers = get_all_careers()
    assert len(careers) == 12, f"Expected 12 careers, found {len(careers)}"
    
    expected_ids = {
        "frontend", "backend", "fullstack", "mobile",
        "data_analyst", "data_scientist", "ai_ml", "devops_cloud",
        "cybersecurity", "qa_automation", "ui_ux", "data_engineer"
    }
    actual_ids = {c["id"] for c in careers}
    assert actual_ids == expected_ids, f"Career IDs mismatch: {actual_ids ^ expected_ids}"

    for c in careers:
        assert "title" in c and len(c["title"]) > 0
        assert "description" in c
        assert "key_skills" in c and len(c["key_skills"]) >= 3
        assert "difficulty" in c
        assert "salary_range" in c
        assert "why_matches" in c

def test_career_questions_count():
    questions = get_career_questions()
    assert len(questions) == 15, f"Expected exactly 15 career assessment questions, found {len(questions)}"
    for q in questions:
        assert "id" in q
        assert "question" in q
        assert "feature_key" in q
        assert "options" in q and len(q["options"]) >= 2

def test_ml_prediction_fullstack_persona():
    answers = {
        "math_enjoyment": 3,
        "programming_enjoyment": 5,
        "ui_design_enjoyment": 4,
        "logic_problem_solving": 5,
        "data_preference": 4,
        "cloud_infra_enjoyment": 3,
        "cybersecurity_enjoyment": 3,
        "statistics_comfort": 3,
        "build_vs_analyze": "build_user_facing",
        "debugging_enjoyment": 4,
        "learning_time_commitment": "10_to_20_hrs",
        "programming_experience_level": "intermediate",
        "education_background": "cs_degree",
        "work_style_preference": "logic_architecture",
        "career_archetype": "balanced_generalist"
    }

    recs, all_compat = get_career_recommendations(answers, top_k=3)
    assert len(recs) == 3
    assert recs[0]["rank"] == 1
    assert recs[1]["rank"] == 2
    assert recs[2]["rank"] == 3

    # Compatibility scores must be between 50 and 99
    for r in recs:
        assert 50 <= r["compatibility"] <= 99
        assert r["career_id"] in all_compat

    assert len(all_compat) == 12

def test_ml_prediction_data_science_persona():
    answers = {
        "math_enjoyment": 5,
        "programming_enjoyment": 4,
        "ui_design_enjoyment": 1,
        "logic_problem_solving": 5,
        "data_preference": 5,
        "cloud_infra_enjoyment": 2,
        "cybersecurity_enjoyment": 2,
        "statistics_comfort": 5,
        "build_vs_analyze": "research_models",
        "debugging_enjoyment": 3,
        "learning_time_commitment": "20_plus_hrs",
        "programming_experience_level": "intermediate",
        "education_background": "cs_degree",
        "work_style_preference": "data_investigative",
        "career_archetype": "analytical_data"
    }

    recs, _ = get_career_recommendations(answers, top_k=3)
    top_ids = [r["career_id"] for r in recs]
    assert any(cid in ["data_scientist", "ai_ml", "data_analyst"] for cid in top_ids)
