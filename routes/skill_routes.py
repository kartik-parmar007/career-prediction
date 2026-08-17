"""
Skill Routes: Endpoints for 10-MCQ Technical Skill Tests and Evaluation Engine.
"""

from flask import Blueprint, request, jsonify
from utils.json_loader import get_skill_test, get_all_careers

skill_bp = Blueprint("skill_bp", __name__)

AVAILABLE_TECH_TESTS = [
    {"id": "javascript", "title": "JavaScript Mastery", "category": "Technology", "icon": "fa-brands fa-js"},
    {"id": "python", "title": "Python Mastery", "category": "Technology", "icon": "fa-brands fa-python"},
    {"id": "java", "title": "Java Mastery", "category": "Technology", "icon": "fa-brands fa-java"},
    {"id": "react", "title": "React Mastery", "category": "Technology", "icon": "fa-brands fa-react"},
    {"id": "nodejs", "title": "Node.js Mastery", "category": "Technology", "icon": "fa-brands fa-node-js"},
    {"id": "sql", "title": "SQL & Databases", "category": "Technology", "icon": "fa-solid fa-database"},
    {"id": "docker", "title": "Docker & Containers", "category": "Technology", "icon": "fa-brands fa-docker"},
    {"id": "aws", "title": "AWS Cloud Architecture", "category": "Technology", "icon": "fa-brands fa-aws"},
    {"id": "machine_learning", "title": "Machine Learning Foundations", "category": "Technology", "icon": "fa-solid fa-brain"}
]

@skill_bp.route("/api/skill-tests", methods=["GET"])
def list_skill_tests():
    """Returns a catalog of all 12 Career Tests + 9 Technology Tests."""
    try:
        careers = get_all_careers()
        career_tests = [
            {
                "id": c["id"],
                "title": f"{c['title']} Readiness Test",
                "category": "Career Field",
                "icon": c.get("icon", "fa-solid fa-code"),
                "short_description": c.get("short_description", ""),
                "total_questions": 10
            }
            for c in careers
        ]

        tech_tests = [
            {
                "id": t["id"],
                "title": t["title"],
                "category": "Technology",
                "icon": t["icon"],
                "short_description": f"Evaluate your practical {t['title']} knowledge across 10 technical questions.",
                "total_questions": 10
            }
            for t in AVAILABLE_TECH_TESTS
        ]

        return jsonify({
            "status": "success",
            "career_tests": career_tests,
            "tech_tests": tech_tests,
            "total_available": len(career_tests) + len(tech_tests)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@skill_bp.route("/api/skill-tests/<test_id>", methods=["GET"])
def get_test_questions(test_id):
    """
    Returns exactly 10 questions for the selected skill test.
    Hides 'correct_answer' and 'explanation' until submission.
    """
    try:
        test_data = get_skill_test(test_id)
        questions = test_data.get("questions", [])

        # Strict requirement: Exactly 10 questions
        if len(questions) != 10:
            return jsonify({
                "status": "error",
                "message": f"Test configuration invalid: expected exactly 10 questions, found {len(questions)}"
            }), 500

        sanitized_questions = []
        for q in questions:
            sanitized_questions.append({
                "id": q["id"],
                "question": q["question"],
                "options": q["options"],
                "topic": q.get("topic", "General"),
                "difficulty": q.get("difficulty", "medium")
            })

        return jsonify({
            "status": "success",
            "test_id": test_id,
            "title": test_data.get("title", "Skill Assessment"),
            "category": test_data.get("category", "General"),
            "description": test_data.get("description", ""),
            "total_questions": 10,
            "questions": sanitized_questions
        })
    except FileNotFoundError:
        return jsonify({"status": "error", "message": f"Skill test '{test_id}' not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@skill_bp.route("/api/skill-test/evaluate", methods=["POST"])
def evaluate_skill_test():
    """
    Evaluates submitted answers for exactly 10 questions.
    Computes overall score, percentage, topic breakdown, strong and weak areas.
    """
    data = request.get_json() or {}
    test_id = data.get("test_id")
    user_answers = data.get("answers", {})

    if not test_id:
        return jsonify({"status": "error", "message": "Missing test_id"}), 400

    try:
        test_data = get_skill_test(test_id)
        questions = test_data.get("questions", [])

        # Validate that all 10 questions are answered
        if len(questions) != 10:
            return jsonify({"status": "error", "message": "Test integrity error: not 10 questions"}), 500

        answered_count = len(user_answers)
        if answered_count < 10:
            missing_q = [str(q["id"]) for q in questions if str(q["id"]) not in user_answers]
            return jsonify({
                "status": "error",
                "message": f"All 10 questions must be answered before submitting. Missing question(s): {', '.join(missing_q)}",
                "missing_questions": missing_q
            }), 400

        correct_count = 0
        topic_stats = {}
        reviews = []

        for q in questions:
            qid_str = str(q["id"])
            user_choice = user_answers.get(qid_str)
            try:
                user_choice_idx = int(user_choice) if user_choice is not None else -1
            except (ValueError, TypeError):
                user_choice_idx = -1

            correct_idx = q["correct_answer"]
            is_correct = (user_choice_idx == correct_idx)
            if is_correct:
                correct_count += 1

            topic = q.get("topic", "General")
            if topic not in topic_stats:
                topic_stats[topic] = {"total": 0, "correct": 0}
            topic_stats[topic]["total"] += 1
            if is_correct:
                topic_stats[topic]["correct"] += 1

            reviews.append({
                "id": q["id"],
                "question": q["question"],
                "options": q["options"],
                "user_selected": user_choice_idx,
                "correct_answer": correct_idx,
                "is_correct": is_correct,
                "topic": topic,
                "difficulty": q.get("difficulty", "medium"),
                "explanation": q.get("explanation", "")
            })

        score_pct = int((correct_count / 10) * 100)

        # Topic Breakdown %
        topic_breakdown = {}
        strong_areas = []
        weak_areas = []

        for topic, stat in topic_stats.items():
            pct = int((stat["correct"] / stat["total"]) * 100)
            topic_breakdown[topic] = {
                "total": stat["total"],
                "correct": stat["correct"],
                "percentage": pct
            }
            if pct >= 70:
                strong_areas.append(topic)
            else:
                weak_areas.append(topic)

        # Readiness Level
        if score_pct >= 90:
            level = "Advanced / Master"
        elif score_pct >= 70:
            level = "Intermediate / Job Ready"
        elif score_pct >= 50:
            level = "Beginner+"
        else:
            level = "Novice / Foundational"

        return jsonify({
            "status": "success",
            "test_id": test_id,
            "title": test_data.get("title", "Skill Assessment"),
            "category": test_data.get("category", "General"),
            "total_questions": 10,
            "correct_count": correct_count,
            "score_percentage": score_pct,
            "technical_readiness": score_pct,
            "current_level": level,
            "topic_breakdown": topic_breakdown,
            "strong_areas": strong_areas,
            "weak_areas": weak_areas,
            "question_reviews": reviews
        })
    except FileNotFoundError:
        return jsonify({"status": "error", "message": f"Skill test '{test_id}' not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
