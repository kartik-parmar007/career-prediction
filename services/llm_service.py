"""
LLM Service Layer for AI IT Career Advisor.
Provides interface for Roadmap Generation and Career Mentor Chatbot.
Features resilient Demo Mode simulation if OPENAI_API_KEY is not configured or offline.
"""

import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

def is_live_llm_enabled():
    return bool(OPENAI_API_KEY and len(OPENAI_API_KEY) > 10)

def get_openai_client():
    if not is_live_llm_enabled():
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"[LLM Service Warning] OpenAI client initialization failed: {e}")
        return None

def generate_personalized_roadmap_llm(context_data):
    """
    Generates a personalized learning roadmap using OpenAI API, or falls back to intelligent Demo Mode.
    
    context_data structure:
        - career_id
        - career_title
        - compatibility_pct
        - readiness_pct
        - current_level
        - weak_topics (list)
        - strong_topics (list)
        - weekly_hours
        - standard_curriculum (dict of skills/phases from JSON)
    """
    if is_live_llm_enabled():
        try:
            client = get_openai_client()
            if client:
                prompt = build_roadmap_prompt(context_data)
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an elite IT Career Mentor and Technical Curriculum Architect. Return ONLY valid JSON adhering strictly to the requested schema. Do NOT include markdown code fences or conversational prose."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4,
                    response_format={"type": "json_object"}
                )
                raw_content = response.choices[0].message.content
                parsed = json.loads(raw_content)
                if "phases" in parsed and isinstance(parsed["phases"], list):
                    parsed["generated_by"] = "live_ai"
                    return parsed
        except Exception as e:
            print(f"[LLM Service Warning] Live roadmap generation error: {e}. Falling back to rule-based AI synthesis.")

    # Fallback to rich contextual Demo Mode roadmap
    return generate_demo_roadmap(context_data)

def generate_mentor_chat_response(messages_history, session_context):
    """
    Responds to user questions in the AI Career Mentor chatbot with awareness of active session context.
    """
    user_query = ""
    for msg in reversed(messages_history):
        if msg.get("role") == "user":
            user_query = msg.get("content", "")
            break

    if is_live_llm_enabled():
        try:
            client = get_openai_client()
            if client:
                system_prompt = build_mentor_system_prompt(session_context)
                api_messages = [{"role": "system", "content": system_prompt}]
                # Append last 6 turns for context
                for m in messages_history[-6:]:
                    role = "user" if m.get("role") == "user" else "assistant"
                    api_messages.append({"role": role, "content": m.get("content", "")})

                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=api_messages,
                    temperature=0.7,
                    max_tokens=800
                )
                reply = response.choices[0].message.content
                return {
                    "response": reply,
                    "mode": "live_ai",
                    "model": OPENAI_MODEL
                }
        except Exception as e:
            print(f"[LLM Service Warning] Mentor chat API error: {e}. Falling back to demo mode response.")

    # Demo mode fallback response
    demo_reply = generate_demo_mentor_response(user_query, session_context)
    return {
        "response": demo_reply,
        "mode": "demo_mode",
        "model": "AI Mentor Advisor (Demo Mode)"
    }

def build_roadmap_prompt(ctx):
    return f"""
Generate a structured, 6-Phase Personalized Technical Learning Roadmap for:
- Target Career: {ctx.get('career_title', 'Software Engineer')}
- Career Compatibility: {ctx.get('compatibility_pct', 80)}%
- Technical Readiness Score: {ctx.get('readiness_pct', 60)}%
- Current Assessed Level: {ctx.get('current_level', 'Beginner+')}
- Weak Areas to Prioritize: {', '.join(ctx.get('weak_topics', [])) or 'General foundations'}
- Strong Areas Already Known: {', '.join(ctx.get('strong_topics', [])) or 'None yet'}
- Available Study Time: {ctx.get('weekly_hours', '10 hours/week')}

Standard Curriculum Context:
{json.dumps(ctx.get('standard_curriculum', {}), indent=2)}

Requirements:
Return a JSON object with:
1. "career_title": string
2. "custom_summary": string (2-3 sentences explaining how this roadmap specifically targets their weak areas and builds toward career readiness)
3. "total_estimated_months": string (e.g. "5 - 7 Months")
4. "phases": array of 6 phase objects, each containing:
   - "phase": integer (1 to 6)
   - "title": string
   - "duration": string (e.g. "3 - 4 Weeks")
   - "focus_tag": string (e.g. "Priority Gap", "Core Skill", "Advanced Architecture", "Capstone")
   - "skills": array of 3-5 strings
   - "topics": array of 3-5 strings
   - "practice_tasks": array of 2 strings
   - "project": string
   - "milestone": string
"""

def build_mentor_system_prompt(ctx):
    career = ctx.get("selected_career_title", "Software Engineer")
    compat = ctx.get("compatibility_pct", "N/A")
    readiness = ctx.get("readiness_pct", "N/A")
    weak = ", ".join(ctx.get("weak_topics", [])) or "None identified yet"
    strong = ", ".join(ctx.get("strong_topics", [])) or "General tech foundations"

    return f"""
You are the AI IT Career Mentor — an encouraging, knowledgeable, and pragmatic senior technology director and career counselor.
You are counseling a student/professional with the following live assessment profile:
- Target Career Goal: {career}
- Career Compatibility Fit: {compat}%
- Technical Readiness Score: {readiness}%
- Verified Strong Topics: {strong}
- Priority Areas Needing Improvement: {weak}

Guidelines:
1. Ground your advice directly in the user's specific weak topics, target career, and readiness level.
2. Provide concrete, actionable technical guidance with real code concepts, best practices, and project suggestions.
3. Be supportive, realistic, and inspiring. Keep answers structured, readable (with bullet points where appropriate), and concise (2-4 paragraphs).
4. Never give generic boilerplate; customize your explanation to their career path.
"""

def generate_demo_roadmap(ctx):
    """
    Intelligent rule-based roadmap synthesizer that adapts canonical roadmap blueprints
    to emphasize user weak topics and adjust durations based on study hours.
    """
    from utils.json_loader import get_roadmaps_data
    roadmaps = get_roadmaps_data()
    career_id = ctx.get("career_id", "frontend")
    base_roadmap = roadmaps.get(career_id, roadmaps.get("frontend"))

    career_title = ctx.get("career_title", base_roadmap.get("career_title", "IT Specialist"))
    weak_topics = ctx.get("weak_topics", [])
    strong_topics = ctx.get("strong_topics", [])
    readiness = ctx.get("readiness_pct", 70)
    weekly_hours = ctx.get("weekly_hours", "10 hours/week")

    phases = []
    for p in base_roadmap.get("phases", []):
        phase_copy = dict(p)
        phase_num = phase_copy.get("phase", 1)

        # Tag priority phases based on weak topics
        if phase_num == 1 and readiness < 60:
            phase_copy["focus_tag"] = "Urgent Foundation"
        elif phase_num == 2 and weak_topics:
            phase_copy["focus_tag"] = "Priority Gap Closure"
            phase_copy["practice_tasks"].insert(0, f"Dedicated drills targeting: {', '.join(weak_topics[:2])}")
        elif phase_num >= 5:
            phase_copy["focus_tag"] = "Industry Capstone"
        else:
            phase_copy["focus_tag"] = "Core Mastery"

        phases.append(phase_copy)

    summary = (
        f"Customized for your {career_title} journey ({ctx.get('compatibility_pct', 85)}% fit, {readiness}% technical readiness). "
        f"This curriculum prioritizes your identified improvement areas ({', '.join(weak_topics[:3]) if weak_topics else 'core architecture'}) "
        f"while accelerating through concepts you've already demonstrated ({', '.join(strong_topics[:2]) if strong_topics else 'foundations'}). "
        f"Paced for {weekly_hours}."
    )

    return {
        "career_title": career_title,
        "custom_summary": summary,
        "total_estimated_months": "5 - 7 Months (at 10-15 hrs/week)",
        "generated_by": "demo_ai_simulation",
        "phases": phases
    }

def generate_demo_mentor_response(query, ctx):
    """
    Context-aware response generator for demo mode queries.
    """
    query_lower = query.lower()
    career = ctx.get("selected_career_title", "IT Career")
    weak = ctx.get("weak_topics", [])
    readiness = ctx.get("readiness_pct", 70)

    if "what should i learn first" in query_lower or "where do i start" in query_lower or "start" in query_lower:
        first_step = weak[0] if weak else "core language fundamentals"
        return (
            f"Based on your current readiness score ({readiness}%) for **{career}**, "
            f"your highest leverage starting point is mastering **{first_step}**.\n\n"
            f"Here is your recommended 3-step action plan for this week:\n"
            f"1. **Isolate the concept**: Spend 3-4 focused hours building small test scripts or UI components dedicated purely to {first_step}.\n"
            f"2. **Build a mini-project**: Do not just watch tutorials — write a standalone project that enforces this concept from scratch.\n"
            f"3. **Retake the technical skill test**: Validate that your score on this topic improves to 80%+."
        )

    if "project" in query_lower or "portfolio" in query_lower or "build" in query_lower:
        return (
            f"For a standout **{career}** portfolio, recruiters want to see end-to-end problem solving rather than clone tutorials.\n\n"
            f"**Recommended Project Blueprint:**\n"
            f"• **Project Name**: Multi-Tenant Real-Time Analytics & Operations Dashboard\n"
            f"• **Core Architecture**: Interactive UI + REST/GraphQL API + Relational Database + Automated CI/CD\n"
            f"• **Key Feature to Highlight**: Specifically showcase error handling and state management for **{', '.join(weak[:2]) if weak else 'complex data flows'}**.\n"
            f"• **Deployment**: Ship it live with a public GitHub repository, automated test suite, and a clear architectural diagram in your README."
        )

    if "how long" in query_lower or "time" in query_lower or "duration" in query_lower:
        return (
            f"With your current profile ({readiness}% readiness in {career}), here is a realistic timeline breakdown:\n\n"
            f"• **At 10 hours/week**: ~5 to 6 months to achieve job-ready competency and complete 2 portfolio capstones.\n"
            f"• **At 20+ hours/week (Bootcamp pace)**: ~3 to 4 months.\n\n"
            f"The key to cutting this timeline in half is deliberate practice on your weak areas (**{', '.join(weak[:2]) if weak else 'systems design'}**) rather than re-studying what you already know."
        )

    if "suitable" in query_lower or "can i" in query_lower or "why" in query_lower:
        return (
            f"**{career}** is an exceptional match for your profile!\n\n"
            f"Your questionnaire responses highlight strong alignment with the problem-solving and analytical patterns demanded in this role. "
            f"While your test highlighted gaps in {', '.join(weak[:2]) if weak else 'advanced topics'}, technical skills are completely learnable with structured roadmaps.\n\n"
            f"What matters most is consistent iterative building. You already have the foundational logic required to excel."
        )

    # General contextual response
    return (
        f"As your AI Career Mentor for **{career}**, I'm here to guide your transition every step of the way.\n\n"
        f"Right now, your profile shows **{readiness}% technical readiness** with priority growth opportunities in **{', '.join(weak[:2]) if weak else 'advanced architecture'}**.\n\n"
        f"Feel free to ask me about:\n"
        f"• Breaking down complex technical concepts step-by-step\n"
        f"• Tailored project architectures to impress hiring managers\n"
        f"• How to structure your weekly study sessions for maximum retention\n"
        f"• Technical interview preparation strategies for {career}"
    )
