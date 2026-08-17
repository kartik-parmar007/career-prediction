"""
Integration tests for Flask Web Application routes and API endpoints.
"""

import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_page_routes_render_ok(client):
    routes = [
        "/",
        "/career-test",
        "/career-result",
        "/skill-tests",
        "/skill-test",
        "/skill-result",
        "/roadmap",
        "/mentor"
    ]
    for r in routes:
        res = client.get(r)
        assert res.status_code == 200, f"Route {r} failed with status {res.status_code}"

def test_health_check_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["database_free"] is True
    assert data["auth_free"] is True

def test_career_api_endpoints(client):
    # List careers
    res = client.get("/api/careers")
    assert res.status_code == 200
    assert len(res.get_json()["careers"]) == 12

    # Specific career
    res = client.get("/api/careers/fullstack")
    assert res.status_code == 200
    assert res.get_json()["career"]["title"] == "Full Stack Developer"

    # Non-existent career
    res = client.get("/api/careers/invalid_career")
    assert res.status_code == 404

    # Career questions
    res = client.get("/api/career-questions")
    assert res.status_code == 200
    assert len(res.get_json()["questions"]) == 15

def test_skill_api_endpoints(client):
    # List skill tests
    res = client.get("/api/skill-tests")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["career_tests"]) == 12
    assert len(data["tech_tests"]) == 9

    # Specific skill test questions (must return 10)
    res = client.get("/api/skill-tests/python")
    assert res.status_code == 200
    test_obj = res.get_json()
    assert len(test_obj["questions"]) == 10
    # verify correct_answer is hidden from public fetch
    assert "correct_answer" not in test_obj["questions"][0]

def test_ai_roadmap_generation_endpoint(client):
    payload = {
        "career_id": "frontend",
        "career_title": "Frontend Developer",
        "compatibility_pct": 85,
        "readiness_pct": 70,
        "weak_topics": ["React Hooks", "Web Security"],
        "strong_topics": ["HTML5 Semantics", "CSS Box Model"],
        "weekly_hours": "10 hours/week"
    }
    res = client.post("/api/ai/roadmap", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "phases" in data["roadmap"]
    assert len(data["roadmap"]["phases"]) >= 6

def test_ai_mentor_chat_endpoint(client):
    payload = {
        "messages": [
            {"role": "user", "content": "What should I learn first for Full Stack development?"}
        ],
        "session_context": {
            "selected_career_title": "Full Stack Developer",
            "readiness_pct": 70,
            "weak_topics": ["React", "SQL"]
        }
    }
    res = client.post("/api/ai/chat", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "message" in data
    assert len(data["message"]["content"]) > 10
