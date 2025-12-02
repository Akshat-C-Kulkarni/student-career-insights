# 🎓 Student Career Insights AI Chatbot
An AI-powered conversational assistant that helps students explore career paths, required skills, roadmaps, project ideas, and role comparisons — built as part of the 4 Weeks – 4 Projects Challenge (Week 4).

## 🚀 Project Overview
The Student Career Insights AI Chatbot is a Streamlit-based web application that provides personalized career guidance to students.

### It combines:
- Rule-based intent recognition
- Structured knowledge datasets (roles, roadmaps, skills, projects)
- LLM-powered dynamic reasoning (via OpenRouter)
- Clean UI with persistent chat history

### Students can ask queries like:
- “What skills are required for Data Scientist?”
- “Roadmap for Machine Learning Engineer”
- “Frontend vs Backend Developer”
- “Give me project ideas for Cloud Engineer”
- “Resume tips please”
The chatbot returns formatted, actionable insights with an intuitive chat UI.

## 🎯 Features
###Conversational Career Guidance
Supports queries across skills, roadmaps, projects, role explanations, comparisons, and resume tips.

### Hybrid Intelligence System
- Deterministic rule-based responses
- Knowledge lookup from curated datasets
- LLM expansion when more detail is needed

### Beautiful Chat UI (Streamlit)
- Dark-themed user and assistant bubbles
- Fixed bottom input bar
- Auto-clearing input
- Smooth session flow

### Session Persistence
All chats can be saved to /data/sessions/ as JSON files.

### Dataset Integration
Raw structured datasets for roles, skills, roadmaps, and projects stored under:
data/raw/

### Demo-ready
A demo video is included under:
demo/demo_video.mp4

## 📂 Project Structure
student-career-insights/ <br>
│ <br>
├── app/ <br>
│   ├── main.py                 # Streamlit UI <br>
│   ├── backend.py              # Intent + response logic <br>
│   ├── llm.py                  # OpenRouter / LLM wrapper <br>
│ <br>
├── data/ <br>
│   ├── role_skill_map.json     # Merged structured knowledge <br>
│   ├── raw/                    # Raw curated datasets <br>
│   │   ├── project_ideas.csv <br>
│   │   ├── roadmaps.csv <br>
│   │   ├── roles.csv <br>
│   │   ├── skills.xlsx <br>
│   ├── sessions/               # Auto-saved chat histories <br>
│ <br>
├── demo/ <br>
│   ├── demo_video.mp4 <br>
│ <br>
├── docs/ <br>
│   ├── flow.png                # App architecture diagram <br>
│   ├── llm_config.md           # API setup <br>
│   ├── USER_GUIDE.md           # How to use the app <br>
│ <br>
├── notebooks/ <br>
│   ├── intent_tests.ipynb      # Unit tests for intent recognition <br>
│ <br>
├── scripts/ <br>
│   ├── test_llm.py             # API test script <br>
│   ├── run_demo.py             # Automated demo script <br>
│ <br>
├── requirements.txt <br>
├── README.md <br>
└── .gitignore <br>

## 🧠 Tech Stack
### Frontend & App Framework
- Streamlit
### Backend & Logic
- Python
- Intent recognition (regex + rule-based)
- Knowledge graph from structured datasets
### LLM Integration
- OpenRouter API
- mistralai/mistral-7b-instruct (free-tier)

## 🔧 Installation & Setup
### 1️⃣ Clone the repository
git clone https://github.com/<your-username>/student-career-insights.git
cd student-career-insights

### 2️⃣ Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

### 3️⃣ Install dependencies
pip install -r requirements.txt

### 4️⃣ Set your OpenRouter API key
setx OPENROUTER_API_KEY "your_key_here"  # Windows
export OPENROUTER_API_KEY="your_key_here"  # Mac/Linux

### 5️⃣ Run the app
streamlit run app/main.py

## 📝 How to Use
1. Type any career-related question into the chat box.
2. Examples:
    - “Skills for Data Analyst”
    - “Explain Machine Learning Engineer in detail”
    - “Project ideas for Backend Developer”
    - “Data Scientist vs Data Analyst”
    - “Roadmap for UI/UX Designer”
3. Chat is saved via Save Chat button in the sidebar.

## 📹 Demo Video
A quick walkthrough of the chatbot is available at:
demo/demo_video.mp4

## 📌 Future Improvements
- Add embeddings-based semantic search
- Add role clustering using KMeans
- Multi-turn role exploration (career tree)
- Export chat as PDF
- Add light mode / theme customization

## 🏆 Author
Akshat C Kulkarni
B.Tech CSE (AI & ML) | 4 Week – 4 Project Challenge
GitHub • LinkedIn • Portfolio (links to be added)