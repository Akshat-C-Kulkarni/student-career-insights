import json
import os
import re
from typing import Optional

# Import LLM caller you implemented
from llm import call_openrouter_chat

# ---------------------------------------
# Load role → skills → roadmap → projects
# ---------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "role_skill_map.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    ROLE_DATA = json.load(f)

# ---------------------------------------
# SANITIZATION FUNCTION (NEW)
# ---------------------------------------
def clean_llm_text(text: str) -> str:
    """
    Removes instruction tokens and unwanted artifacts
    returned by some OpenRouter providers.
    """
    if not text:
        return text

    patterns = [
        r"<s>", r"</s>",
        r"\[INST\]", r"\[/INST\]",
        r"\[B_INST\]", r"\[/B_INST\]",
        r"<<SYS>>", r"<</SYS>>",
        r"<\|im_start\|>", r"<\|im_end\|>",
        r"<\|assistant\|>", r"<\|user\|>",
        r"</?think>", r"</?think_detail>"
    ]

    cleaned = text
    for pat in patterns:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.strip()
    return cleaned

# ---------------------------------------
# Intent detection (regex-based)
# ---------------------------------------
INTENT_KEYWORDS = {
    "role_info": [
        r"\bwhat is\b", r"\bexplain\b", r"\brole of\b", r"\bwho is a\b", r"\bjob role\b"
    ],
    "skills_needed": [
        r"\bskills\b", r"\bwhat skills\b", r"\brequired skills\b", r"\bskillset\b", r"\bcompetencies\b"
    ],
    "roadmap": [
        r"\broadmap\b", r"\blearning path\b", r"\bhow to start\b", r"\bsteps to\b", r"\bget started\b"
    ],
    "projects": [
        r"\bproject ideas\b", r"\bprojects\b", r"\bproject for\b", r"\bbuild a\b", r"\bproject suggestions\b"
    ],
    "compare_roles": [
        r"\bvs\b", r"\bdifference between\b", r"\bcompare\b", r"\bversus\b"
    ],
    "resume_tip": [
        r"\bresume\b", r"\bcv\b", r"\bcover letter\b", r"\bhow to write (a )?resume\b", r"\bresume tips\b"
    ],
}

COMPILED_INTENT_PATTERNS = {
    intent: [re.compile(pat, flags=re.IGNORECASE) for pat in patterns]
    for intent, patterns in INTENT_KEYWORDS.items()
}

def get_intent(message: str) -> str:
    msg = (message or "").strip()
    if not msg:
        return "general"

    # High priority: compare_roles
    for pat in COMPILED_INTENT_PATTERNS["compare_roles"]:
        if pat.search(msg):
            return "compare_roles"

    # High priority: resume tips
    for pat in COMPILED_INTENT_PATTERNS["resume_tip"]:
        if pat.search(msg):
            return "resume_tip"

    # Priority order for other intents
    priority_order = ["skills_needed", "roadmap", "projects", "role_info"]
    for intent in priority_order:
        for pat in COMPILED_INTENT_PATTERNS[intent]:
            if pat.search(msg):
                return intent

    return "general"

# ---------------------------------------
# Role extraction
# ---------------------------------------
def extract_role_from_text(message: str) -> Optional[str]:
    msg = (message or "").lower()
    for role in ROLE_DATA.keys():
        if role.lower() in msg:
            return role
    return None

# ---------------------------------------
# Helper: detect expansion request
# ---------------------------------------
EXPAND_KEYWORDS = re.compile(
    r"\b(explain|detail|detailed|elaborate|why|how to|more|expand)\b",
    flags=re.IGNORECASE
)

def user_wants_expansion(message: str) -> bool:
    return bool(EXPAND_KEYWORDS.search(message or ""))

# ---------------------------------------
# Prompt templates
# ---------------------------------------
SYSTEM_PROMPT_BRIEF = (
    "You are a concise, helpful assistant that provides clear, actionable career advice for students. "
    "Keep answers professional and practical."
)

PROMPT_TEMPLATES = {
    "role_summary": (
        "You are writing a clean, structured **Markdown** summary.\n"
        "Follow this exact format:\n\n"
        "### Overview\n"
        "- (2–3 sentences)\n\n"
        "### Responsibilities\n"
        "- Bullet points\n\n"
        "### Core Skills\n"
        "- Bullet points\n\n"
        "### Beginner Advice\n"
        "- Bullet points\n\n"
        "Role: **{role}**"
    ),

    "roadmap_expansion": (
        "Expand this learning roadmap with short, clear Markdown sections.\n"
        "For each step, add 2–3 bullet points with practical suggestions.\n\n"
        "### Roadmap\n"
        "{roadmap}\n\n"
        "Role: **{role}**"
    ),

    "projects_expansion": (
        "The user needs expanded Markdown project descriptions.\n"
        "For each project, follow this EXACT format:\n\n"
        "### <Project Name>\n"
        "- What the project does\n"
        "- Tools/technologies to use\n"
        "- What the student learns\n\n"
        "Projects: {projects}\n"
        "Role: **{role}**"
    ),

    "compare_roles": (
        "Write a clean, well-formatted Markdown comparison.\n"
        "Follow this exact structure:\n\n"
        "### Overview\n"
        "- Short explanation\n\n"
        "### {role_a}\n"
        "**Responsibilities**\n"
        "- Bullet points\n"
        "**Core Skills**\n"
        "- Bullet points\n"
        "**Beginner Projects**\n"
        "- Bullet points\n\n"
        "### {role_b}\n"
        "**Responsibilities**\n"
        "- Bullet points\n"
        "**Core Skills**\n"
        "- Bullet points\n"
        "**Beginner Projects**\n"
        "- Bullet points\n\n"
        "Keep the answer under 350 words."
    ),

    "general_advice": (
        "Provide clean, simple Markdown advice.\n"
        "Use headings and bullet points.\n"
        "Keep it practical and helpful.\n\n"
        "Question: {question}"
    )
}

# ---------------------------------------
# LLM Call wrapper (UPDATED with sanitization)
# ---------------------------------------
def call_llm_for_template(template_key: str, user_message: str, model: str = None, max_tokens: int = 256):
    system = {"role": "system", "content": SYSTEM_PROMPT_BRIEF}

    if template_key in PROMPT_TEMPLATES:
        user_content = PROMPT_TEMPLATES[template_key].format(**user_message)
    else:
        user_content = PROMPT_TEMPLATES["general_advice"].format(question=user_message)

    messages = [
        system,
        {"role": "user", "content": user_content}
    ]

    result = call_openrouter_chat(messages=messages, model=model or None, max_tokens=max_tokens)

    if not result.get("ok"):
        return None, result

    content = clean_llm_text(result.get("content", ""))

    if len(content) > 4000:
        content = content[:4000] + "..."

    return content, result

# ---------------------------------------
# Main response generation (hybrid logic)
# ---------------------------------------
def get_response(message: str, intent: str):
    message = (message or "").strip()
    role = extract_role_from_text(message)

    # ---------- Deterministic Answers ----------
    if intent == "skills_needed":
        if role:
            skills = ROLE_DATA[role]["skills"]
            base = "### 🧠 Key Skills for **{}**\n{}\n\n".format(
                role, "\n".join(f"- {s}" for s in skills)
            )

            if user_wants_expansion(message):
                payload = {"role": role}
                expanded, _ = call_llm_for_template(
                    "role_summary",
                    payload,
                    model="mistralai/mistral-7b-instruct",
                    max_tokens=220
                )
                if expanded:
                    return base + expanded


            return base + "If you want, ask for a roadmap or project ideas."

        return "### 🧠 To list skills, I need a role. Try: *What skills are required for Data Scientist?*"

    if intent == "roadmap":
        if role:
            roadmap = ROLE_DATA[role]["roadmap"]
            base = "### 🗺️ Learning Roadmap for **{}**\n{}\n\n".format(
                role, "\n".join(f"{i+1}. {step}" for i, step in enumerate(roadmap))
            )

            if user_wants_expansion(message):
                payload = {"role": role, "roadmap": "\n".join(roadmap)}
                expanded, _ = call_llm_for_template(
                    "roadmap_expansion",
                    payload,
                    model="mistralai/mistral-7b-instruct",
                    max_tokens=240
                )
                if expanded:
                    return base + expanded

            return base + "Ask me to expand any step if you'd like more detail."

        return "### 🗺️ I can give you a roadmap, but I need a role. Try: *Roadmap for Frontend Developer*"

    if intent == "projects":
        if role:
            projects = ROLE_DATA[role]["projects"]
            base = "### 💡 Project Ideas for **{}**\n{}\n\n".format(
                role, "\n".join(f"- {p}" for p in projects)
            )

            if user_wants_expansion(message):
                payload = {"role": role, "projects": "\n".join(projects)}
                expanded, _ = call_llm_for_template(
                    "projects_expansion",
                    payload,
                    model="mistralai/mistral-7b-instruct",
                    max_tokens=240
                )

                if expanded:
                    return base + expanded

            return base + "If you want, ask me to explain any project in detail."

        return "### 💡 To suggest the best project ideas, I need a role. Try: *Project ideas for Full Stack Developer*"

    if intent == "role_info":
        if role:
            skills = ROLE_DATA[role]["skills"]
            base = f"### 📘 About the Role: **{role}**\n"
            base += (
                f"{role}s typically work on tasks requiring both technical and analytical skills.\n\n"
                "**Core Skills:**\n" + "\n".join(f"- {s}" for s in skills) + "\n\n"
            )

            if user_wants_expansion(message):
                payload = {"role": role}
                expanded, _ = call_llm_for_template("role_summary", payload, max_tokens=220)
                if expanded:
                    return base + expanded

            return base + "I can also provide a roadmap or project ideas."

        return "### 📘 I can explain any tech role, but please mention it. Example: *What is a Data Analyst?*"

    # ---------- Role Comparison ----------
    if intent == "compare_roles":
        msg_low = message.lower()
        matched_roles = [role for role in ROLE_DATA.keys() if role.lower() in msg_low]

        if len(matched_roles) >= 2:
            role_a, role_b = matched_roles[:2]
        else:
            parts = re.split(r"\bvs\b|\bversus\b|\band\b|\/|,|\-", message, flags=re.IGNORECASE)
            if len(parts) >= 2:
                role_a = parts[0].strip()
                role_b = parts[1].strip()
            else:
                role_a = None
                role_b = None

        payload = {
            "role_a": role_a or "Role A",
            "role_b": role_b or "Role B"
        }

        llm_out, _ = call_llm_for_template(
            "compare_roles",
            payload,
            model="mistralai/mistral-7b-instruct",
            max_tokens=260
        )

        if llm_out:
            return "### ⚖️ Role Comparison\n\n" + llm_out

        return (
            "### ⚖️ Role Comparison (temporary fallback)\n"
            "I couldn't reach the LLM right now. Try asking again."
        )

    # ---------- Resume Tips ----------
    if intent == "resume_tip":
        return (
            "### 📄 Resume Tips\n"
            "- Keep it one page\n"
            "- Highlight 5–6 relevant skills\n"
            "- Add 2–3 good projects\n"
            "- Use strong action verbs\n"
            "- Tailor it to the role\n"
            "- Add GitHub + LinkedIn links\n\n"
            "Need help writing bullets? Ask: 'Help me write a resume bullet for my project on X.'"
        )

    # ---------- General → LLM ----------
    if intent == "general":
        payload = {"question": message}
        llm_out, _ = call_llm_for_template(
            "general_advice",
            payload,
            model="mistralai/mistral-7b-instruct",
            max_tokens=260
        )
        if llm_out:
            return "### 💬 Answer\n\n" + llm_out

        return (
            "I can help with skills, roadmaps, project ideas, role explanations, and resume tips. "
            "Try: 'What skills are needed for Data Scientist?'"
        )

    return (
        "### 👋 I can help you explore tech careers!\n"
        "Ask about skills, roadmaps, project ideas, roles, or resume tips."
    )
