import json
import os
import re

# ---------------------------------------
# Load role → skills → roadmap → projects
# ---------------------------------------

# Build absolute path to the JSON file, regardless of where Streamlit runs from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "role_skill_map.json")

with open(DATA_PATH, "r") as f:
    ROLE_DATA = json.load(f)


# ---------------------------------------
# Intent patterns (Task 1)
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

# Compile regex patterns for speed
COMPILED_INTENT_PATTERNS = {
    intent: [re.compile(pat, flags=re.IGNORECASE) for pat in patterns]
    for intent, patterns in INTENT_KEYWORDS.items()
}


# ---------------------------------------
# Intent Detection Function
# ---------------------------------------

def get_intent(message: str) -> str:
    """Rule-based intent detector using regex patterns."""
    msg = message.strip()
    if not msg:
        return "general"

    # Priority 1 → compare
    for pat in COMPILED_INTENT_PATTERNS["compare_roles"]:
        if pat.search(msg):
            return "compare_roles"

    # Priority 2 → resume tips
    for pat in COMPILED_INTENT_PATTERNS["resume_tip"]:
        if pat.search(msg):
            return "resume_tip"

    # Priority 3 → skill, roadmap, project, role_info
    priority_order = ["skills_needed", "roadmap", "projects", "role_info"]
    for intent in priority_order:
        for pat in COMPILED_INTENT_PATTERNS[intent]:
            if pat.search(msg):
                return intent

    # Fallback
    return "general"


# ---------------------------------------
# Role Extraction
# ---------------------------------------

def extract_role_from_text(message: str):
    """Find a role name inside the user message."""
    msg = message.lower()

    for role in ROLE_DATA.keys():
        if role.lower() in msg:
            return role

    return None


# ---------------------------------------
# Response Generator
# ---------------------------------------
def get_response(message: str, intent: str):
    """Deterministic response generation with improved templated replies."""
    role = extract_role_from_text(message)

    # -----------------------------
    # Skills Intent
    # -----------------------------
    if intent == "skills_needed":
        if role:
            skills = ROLE_DATA[role]["skills"]
            return (
                f"### 🧠 Key Skills for **{role}**\n"
                + "\n".join([f"- {s}" for s in skills]) +
                "\n\nIf you want, I can also share a roadmap or project ideas."
            )
        else:
            return (
                "### 🧠 To list the right skills, I need a specific role.\n"
                "**Example roles you can ask about:**\n"
                "- Data Scientist\n- Machine Learning Engineer\n- Backend Developer\n- Frontend Developer\n\n"
                "Try: **What skills are required for Data Scientist?**"
            )

    # -----------------------------
    # Roadmap Intent
    # -----------------------------
    if intent == "roadmap":
        if role:
            roadmap = ROLE_DATA[role]["roadmap"]
            return (
                f"### 🗺️ Learning Roadmap for **{role}**\n"
                + "\n".join([f"1. {step}" if i == 0 else f"{i+1}. {step}"
                             for i, step in enumerate(roadmap)]) +
                "\n\nLet me know if you want resources or project ideas for this role."
            )
        else:
            return (
                "### 🗺️ I can give you a roadmap, but I need a role.\n"
                "Try asking something like:\n"
                "- **Roadmap for Frontend Developer**\n"
                "- **How to start as a Cloud Engineer?**"
            )

    # -----------------------------
    # Projects Intent
    # -----------------------------
    if intent == "projects":
        if role:
            projects = ROLE_DATA[role]["projects"]
            return (
                f"### 💡 Project Ideas for **{role}**\n"
                + "\n".join([f"- {p}" for p in projects]) +
                "\n\nWant me to explain any project in detail?"
            )
        else:
            return (
                "### 💡 To suggest the best project ideas, I need a role.\n"
                "Try:\n- **Project ideas for Full Stack Developer**\n- **Projects for Cloud Engineer**"
            )

    # -----------------------------
    # Role Information Intent
    # -----------------------------
    if intent == "role_info":
        if role:
            skills = ROLE_DATA[role]["skills"]
            return (
                f"### 📘 About the Role: **{role}**\n"
                f"{role}s typically work on tasks requiring both technical and analytical skills.\n\n"
                f"**Core Skills:**\n"
                + "\n".join([f"- {s}" for s in skills]) +
                "\n\nI can also provide a roadmap or project ideas."
            )
        else:
            return (
                "### 📘 I can explain any tech role, but please mention it.\n"
                "Example: **What is a Data Analyst?**"
            )

    # -----------------------------
    # Compare Roles Intent
    # -----------------------------
    if intent == "compare_roles":
        return (
            "### ⚖️ Role Comparison Feature Coming Soon\n"
            "Ask me something like:\n- **Data Scientist vs Data Analyst**\n- **Frontend vs Backend Developer**"
        )

    # -----------------------------
    # Resume Tips Intent
    # -----------------------------
    if intent == "resume_tip":
        return (
            "### 📄 Resume Tips\n"
            "- Keep it one page\n"
            "- Highlight 5–6 relevant skills\n"
            "- Add 2–3 good projects\n"
            "- Use strong action verbs\n"
            "- Tailor it to the role\n"
            "- Add GitHub + LinkedIn links\n\n"
            "Need help with resume bullet points?"
        )

    # -----------------------------
    # Fallback
    # -----------------------------
    return (
        "### 👋 I can help you explore tech careers!\n\n"
        "Try asking about:\n"
        "- Skills for a role\n"
        "- Learning roadmaps\n"
        "- Project ideas\n"
        "- Role explanations\n"
        "- Resume tips\n"
        "For example: **What skills are needed for Data Scientist?**"
    )
