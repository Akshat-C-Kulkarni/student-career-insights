import streamlit as st
from backend import get_intent, get_response
import json, os
from datetime import datetime

# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(page_title="Career Insights Chatbot", page_icon="🎓", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS_DIR = os.path.join(BASE_DIR, "data", "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)


# -----------------------------------------------------
# SESSION STATE
# -----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------------------------------
# SAVE SESSION
# -----------------------------------------------------
def save_session():
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    filepath = os.path.join(SESSIONS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, indent=2)


# -----------------------------------------------------
# CSS STYLES
# -----------------------------------------------------
st.markdown("""
<style>

    /* Chat bubbles */
    .bubble {
        padding: 12px 16px;
        border-radius: 12px;
        margin: 10px 0;
        max-width: 90%;
        display: flex;
        gap: 10px;
        line-height: 1.45;
        color: white;
    }

    .user-bubble { background: #000; }
    .assistant-bubble { background: #2e2e2e; }

    .label {
        font-weight: bold;
        white-space: nowrap;
    }

    /* Fix Streamlit chat_input at bottom */
    .stChatInputContainer {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background-color: #111 !important;
        padding: 15px 25px !important;
        box-shadow: 0 -4px 15px rgba(0,0,0,0.4);
        z-index: 999999 !important;
    }

</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# SIDEBAR
# -----------------------------------------------------
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This chatbot helps students explore careers using:  
    • Rule-based intents  
    • Curated datasets  
    • LLM expansion  
    """)

    st.subheader("💬 Try asking:")
    st.write("""
    • Skills for Data Scientist  
    • Backend vs Frontend  
    • Roadmap for ML Engineer  
    • Resume tips  
    """)

    if st.button("💾 Save Chat"):
        save_session()
        st.success("Saved to data/sessions/")


# -----------------------------------------------------
# HEADER
# -----------------------------------------------------
st.title("🎓 Student Career Insights AI Chatbot")
st.caption("Ask about roles, skills, learning paths, comparisons, or resume tips.")


# -----------------------------------------------------
# DISPLAY CHAT MESSAGES
# -----------------------------------------------------
for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.markdown(
            """
            <div class="bubble user-bubble">
                <div class="label">🧑‍🎓 You:</div>
                <div class="bubble-content">
            """,
            unsafe_allow_html=True
        )
        st.markdown(msg["content"], unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    else:
        st.markdown(
            """
            <div class="bubble assistant-bubble">
                <div class="label">🤖 Assistant:</div>
                <div class="bubble-content">
            """,
            unsafe_allow_html=True
        )
        st.markdown(msg["content"], unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

# -----------------------------------------------------
# CHAT INPUT (Streamlit-native)
# -----------------------------------------------------
user_msg = st.chat_input("Type your message...")

if user_msg:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_msg})

    # Generate assistant reply
    intent = get_intent(user_msg)
    reply = get_response(user_msg, intent)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Rerun to refresh UI
    st.rerun()
