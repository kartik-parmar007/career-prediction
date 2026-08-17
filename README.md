# AI IT Career Advisor 🚀

A modern, production-grade **AI IT Career Advisor** web application built with Python Flask, Scikit-learn, and Vanilla JS / Tailwind CSS.

Features a **15-Question ML Career Recommendation Engine**, **Strict 10-MCQ Technical Readiness Tests** across 12 careers and 9 technologies, **AI-Powered Personalized Learning Roadmaps**, and an **AI Career Mentor Chatbot**.

---

## 🌟 Key Highlights

* **12 Comprehensive IT Careers**: Frontend, Backend, Full Stack, Mobile Developer, Data Analyst, Data Scientist, AI/ML Engineer, DevOps/Cloud, Cybersecurity, QA Automation, UI/UX Designer, Database/Data Engineer.
* **15-Question ML Assessment**: Step-by-step career compatibility evaluation powered by a trained `RandomForestClassifier` (95%+ accuracy) with compatibility percentages.
* **Strictly 10 MCQs Per Skill Test**: Standardized 10-question technical tests across all 12 career fields and 9 technology stacks (JavaScript, Python, Java, React, Node.js, SQL, Docker, AWS, Machine Learning).
* **AI Personalized Roadmaps**: Synthesizes diagnosed skill gaps, current readiness scores, and target curriculum into actionable 6-phase learning plans with tasks, projects, and milestones.
* **AI Career Mentor**: Context-aware advisor chatbot with active session profile awareness.
* **Zero Database & Zero Authentication**: No signup, no passwords, no server-side user data storage. All session state is stored client-side in `localStorage` with a 1-click **Reset Session** action.
* **Demo Mode Ready**: Works out of the box without requiring an API key.

---

## 🏗️ Project Architecture

```text
ai-it-career-advisor/
├── app.py                      # Flask Application Server & Page Routes
├── requirements.txt            # Python Dependencies
├── .env.example                # Environment Variable Template
├── .env                        # Local Environment Configuration
├── README.md                   # Project Documentation
│
├── data/
│   ├── careers.json            # 12 IT Careers Knowledge Base
│   ├── career_questions.json   # 15 General Assessment Questions
│   ├── skills.json             # Skill Taxonomy Mapping
│   ├── roadmaps.json           # Canonical Career Curriculum Blueprints
│   └── skill_tests/            # 21 Test Files (Exactly 10 MCQs each)
│       ├── frontend.json
│       ├── backend.json
│       ├── fullstack.json
│       ├── mobile.json
│       ├── data_analyst.json
│       ├── data_scientist.json
│       ├── ai_ml.json
│       ├── devops_cloud.json
│       ├── cybersecurity.json
│       ├── qa_automation.json
│       ├── ui_ux.json
│       ├── data_engineer.json
│       ├── javascript.json
│       ├── python.json
│       ├── java.json
│       ├── react.json
│       ├── nodejs.json
│       ├── sql.json
│       ├── docker.json
│       ├── aws.json
│       └── machine_learning.json
│
├── ml/
│   ├── data/
│   │   └── career_dataset.csv  # 1,920 Synthetic Benchmark Samples
│   ├── preprocessing.py        # Feature Transformer Pipeline
│   ├── train.py                # Model Selection & Training Script
│   ├── predict.py              # Top-3 Recommendation Inference Module
│   └── model.pkl               # Serialized Joblib Pipeline
│
├── services/
│   ├── ml_service.py           # ML Model Loader & Inference Facade
│   ├── llm_service.py          # OpenAI Client + Resilient Demo Mode Fallback
│   └── roadmap_service.py      # Roadmap Synthesizer
│
├── routes/
│   ├── career_routes.py        # /api/careers, /api/career/predict
│   ├── skill_routes.py         # /api/skill-tests, /api/skill-test/evaluate
│   └── ai_routes.py            # /api/ai/roadmap, /api/ai/chat
│
├── templates/
│   ├── base.html               # Master Layout with Glassmorphism Navbar & Footer
│   ├── index.html              # Modern Hero Landing Page with 12 Career Cards
│   ├── career-test.html        # 15-Question Quiz Stepper + Analysis Modal
│   ├── career-result.html      # Top 3 Matches + 12-Dimension Radar Chart
│   ├── skill-tests.html        # Catalog Hub (12 Careers + 9 Tech Stacks)
│   ├── skill-test.html         # 10-MCQ Runner with Timer & Question Palette
│   ├── skill-result.html       # Readiness %, Level Badge, Topic Chart, Explanations
│   ├── roadmap.html            # Interactive Multi-Phase AI Learning Timeline
│   └── mentor.html             # Context-Aware AI Career Mentor Chatbot
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom Design Tokens, Glassmorphism, Animations
│   └── js/
│       ├── storage.js          # Unified LocalStorage Session Manager
│       ├── main.js             # Global Toast, Mobile Menu, Reset Handler
│       ├── career-test.js      # 15-Question Quiz Stepper Controller
│       ├── skill-test.js       # 10-Question MCQ Test Engine
│       ├── results.js          # Chart.js Visualizations (Radar & Bar)
│       ├── roadmap.js          # AI Roadmap Renderer & Checkbox Tracker
│       └── mentor.js           # AI Chatbot Controller & Prompt Chips
│
└── tests/
    ├── test_career.py          # Career Data & ML Inference Unit Tests
    ├── test_skill.py           # 10-MCQ Structure & Evaluation Unit Tests
    └── test_api.py             # Flask Route & REST API Integration Tests
```

---

## ⚡ Quickstart Guide

### 1. Clone & Setup Environment

```bash
git clone <repo-url>
cd "ai-it-career-advisor"

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

If you wish to use live OpenAI models, set your API key in `.env`:
```env
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
PORT=5000
```
> **Note**: If left blank, the application automatically runs in **Intelligent Demo Mode**, generating realistic contextual roadmaps and mentor advice.

### 3. Train or Verify the ML Model

```bash
python ml/train.py
```

### 4. Run Automated Test Suite

```bash
pytest -v
```

### 5. Launch the Web Application

```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your web browser.

---

## 🧭 Application Flow

```text
Home Page
   ↓
Career Assessment (15 Questions)
   ↓
ML Analysis Modal (Sequential Checkmarks)
   ↓
Top 3 Recommended IT Careers + Radar Chart (Gold / Silver / Bronze)
   ↓
Select ANY Career or Tech Stack
   ↓
Technical Skill Test (Strictly Exactly 10 MCQs)
   ↓
Readiness Score %, Level, Topic Breakdown Chart, Strengths & Gaps, Explanations
   ↓
AI Personalized Learning Roadmap (6 Phases, Practice Tasks, Projects)
   ↓
AI Career Mentor (Live Context-Aware Chatbot)
```

---

## 🛡️ Privacy & Reliability Guarantees

* **No Passwords or Credentials**: Users never submit personal login info.
* **No Database Writes**: No telemetry or user responses are permanently saved on any database server.
* **Instant Session Reset**: Clicking **Reset** in the top navigation immediately wipes all `localStorage` keys and returns to an untracked baseline.
* **Idempotent REST APIs**: Endpoints return clean, deterministic responses formatted for fast client rendering.
