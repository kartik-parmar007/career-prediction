"""
Automated tests for Technical Skill Tests and 10-MCQ Evaluation Engine.
Strictly verifies that all 21 test files have exactly 10 questions and valid structure.
"""

import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.json_loader import get_skill_test, get_data_dir

TEST_IDS = [
    "frontend", "backend", "fullstack", "mobile",
    "data_analyst", "data_scientist", "ai_ml", "devops_cloud",
    "cybersecurity", "qa_automation", "ui_ux", "data_engineer",
    "javascript", "python", "java", "react",
    "nodejs", "sql", "docker", "aws", "machine_learning"
]

def test_all_21_skill_tests_exist_and_have_strictly_10_mcqs():
    assert len(TEST_IDS) == 21

    for test_id in TEST_IDS:
        data = get_skill_test(test_id)
        assert "questions" in data, f"Missing questions in {test_id}.json"
        questions = data["questions"]

        # Critical constraint: Exactly 10 questions per test
        assert len(questions) == 10, f"Skill test '{test_id}' has {len(questions)} questions instead of strictly 10."

        for idx, q in enumerate(questions):
            assert "id" in q and q["id"] == (idx + 1)
            assert "question" in q and len(q["question"]) > 5
            assert "options" in q and len(q["options"]) == 4, f"Question {q['id']} in {test_id} must have 4 options."
            assert "correct_answer" in q and q["correct_answer"] in [0, 1, 2, 3]
            assert "topic" in q and len(q["topic"]) > 0
            assert "explanation" in q and len(q["explanation"]) > 0

def test_skill_test_evaluation_perfect_score():
    from app import create_app
    app = create_app()
    client = app.test_client()

    # Get the react test to find correct answers
    react_data = get_skill_test("react")
    perfect_answers = {str(q["id"]): q["correct_answer"] for q in react_data["questions"]}

    response = client.post("/api/skill-test/evaluate", json={
        "test_id": "react",
        "answers": perfect_answers
    })

    assert response.status_code == 200
    res_json = response.get_json()
    assert res_json["status"] == "success"
    assert res_json["correct_count"] == 10
    assert res_json["score_percentage"] == 100
    assert res_json["technical_readiness"] == 100
    assert len(res_json["strong_areas"]) > 0
    assert len(res_json["weak_areas"]) == 0
    assert len(res_json["question_reviews"]) == 10

def test_skill_test_evaluation_missing_question_rejection():
    from app import create_app
    app = create_app()
    client = app.test_client()

    # Submitting only 9 answers out of 10 must return 400 error
    partial_answers = {str(i): 0 for i in range(1, 10)} # 1 to 9

    response = client.post("/api/skill-test/evaluate", json={
        "test_id": "react",
        "answers": partial_answers
    })

    assert response.status_code == 400
    res_json = response.get_json()
    assert res_json["status"] == "error"
    assert "All 10 questions must be answered" in res_json["message"]
