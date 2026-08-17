"""
AI IT Career Advisor — Flask Application Server.
Serves interactive UI templates and REST API endpoints.
"""

import os
import sys
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure base directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from routes.career_routes import career_bp
from routes.skill_routes import skill_bp
from routes.ai_routes import ai_bp

load_dotenv()

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static")
    )
    CORS(app)

    # Register API Blueprints
    app.register_blueprint(career_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(ai_bp)

    # ---------------- UI Page Routes ----------------

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/career-test")
    def career_test():
        return render_template("career-test.html")

    @app.route("/career-result")
    def career_result():
        return render_template("career-result.html")

    @app.route("/skill-tests")
    def skill_tests():
        return render_template("skill-tests.html")

    @app.route("/skill-test")
    def skill_test_runner():
        return render_template("skill-test.html")

    @app.route("/skill-result")
    def skill_result():
        return render_template("skill-result.html")

    @app.route("/roadmap")
    def roadmap():
        return render_template("roadmap.html")

    @app.route("/mentor")
    def mentor():
        return render_template("mentor.html")

    # ---------------- Health & Diagnostics ----------------

    @app.route("/api/health", methods=["GET"])
    def health_check():
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        has_openai = bool(openai_key and len(openai_key) > 10)
        return jsonify({
            "status": "healthy",
            "app": "AI IT Career Advisor",
            "version": "1.0.0",
            "mode": "live_llm" if has_openai else "demo_mode",
            "database_free": True,
            "auth_free": True
        })

    # ---------------- Error Handlers ----------------

    @app.errorhandler(404)
    def not_found_error(e):
        return render_template("index.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"status": "error", "message": "An internal error occurred. Please refresh or try again."}), 500

    return app

# WSGI application entry for Vercel / Gunicorn
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f">> AI IT Career Advisor running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
