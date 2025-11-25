import json
import os

# Build absolute path to the JSON file, regardless of where Streamlit runs from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "role_skill_map.json")

with open(DATA_PATH, "r") as f:
    ROLE_DATA = json.load(f)

# Keywords for simple rule-based intent classification
INTENTS = {
    "skills": ["skills", "what skills", "required skills"],
    "roadmap": ["roadmap", "learning path", "how to start"],
    "projects": ["project", "project ideas"],
    "compare": ["difference", "compare", "vs"],
    "role_info": ["what is", "explain", "role of"],
}


def get_intent(message: str):
    """Detect user intent based on keywords."""
    msg = message.lower()

    for intent, keywords in INTENTS.items():
        if any(k in msg for k in keywords):
            return intent

    return "general"


def extract_role_from_text(message: str):
    """Find a role name inside the user message."""
    msg = message.lower()

    for role in ROLE_DATA.keys():
        if role.lower() in msg:
            return role

    return None


def get_response(message: str, intent: str):
    """Generate a structured response using rule-based + dataset logic."""
    role = extract_role_from_text(message)

    # Intent-based responses
    if intent == "skills" and role:
        skills = ROLE_DATA[role]["skills"]
        return f"Here are the key skills for **{role}**:\n\n- " + "\n- ".join(skills)

    if intent == "roadmap" and role:
        roadmap = ROLE_DATA[role]["roadmap"]
        return f"Here is the learning roadmap for **{role}**:\n\n- " + "\n- ".join(roadmap)

    if intent == "projects" and role:
        projects = ROLE_DATA[role]["projects"]
        return f"Here are project ideas for **{role}**:\n\n- " + "\n- ".join(projects)

    if intent == "role_info" and role:
        skills = ROLE_DATA[role]["skills"]
        return (
            f"**{role}** is a tech role with responsibilities depending on the company.\n\n"
            f"Here are the core skills required:\n- " + "\n- ".join(skills)
        )

    if intent == "compare":
        return "Comparison feature coming soon (Day 3–4)."

    # If no intent/role matched → give a generic response
    return (
        "I can help you explore tech careers! Ask me about:\n"
        "- Skills for a role (e.g., *What skills are needed for Data Scientist?*)\n"
        "- Roadmaps (e.g., *Roadmap for Frontend Developer*)\n"
        "- Project ideas\n"
        "- Role explanations\n"
        "- Differences between roles\n"
    )
