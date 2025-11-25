import streamlit as st
from backend import get_intent, get_response

# Page setup
st.set_page_config(page_title="Student Career Insights Chatbot", page_icon="🎓", layout="centered")

st.title("🎓 Student Career Insights AI Chatbot")
st.caption("Ask about roles, skills, learning paths, or tech career guidance.")

# Session state to store messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input box
user_input = st.chat_input("Ask me anything about careers...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Backend: intent + response
    intent = get_intent(user_input)
    reply = get_response(user_input, intent)

    # Add bot message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
