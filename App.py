# Import libraries
import os
import streamlit as st
import speech_recognition as sr
import tempfile
from gtts import gTTS
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate,
)
import base64

# Load environment variables
load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

st.set_page_config("🤖SehaatSaathi-Your AI Doctor Health Assistant😷", page_icon="🧠", layout="wide")

# Custom CSS styling
st.markdown("""
<style>
    .main { background-color: #1a1a1a; color: #ffffff; }
    .sidebar .sidebar-content { background-color: #2d2d2d; }
    .stTextInput textarea { color: #ffffff !important; }
    div[role="listbox"] div { background-color: #2d2d2d !important; color: white !important; }
    .chat-message { padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    .chat-message.user { background-color: #4a4a4a; }
    .chat-message.bot { background-color: #3d3d3d; }
</style>
""", unsafe_allow_html=True)

st.title("🤖SehaatSaathi-Your AI Doctor🧑‍⚕️ Smart Health Assistant😷")
st.caption("🚀 Get Instant Medical Advice & Medicine Recommendations🤷‍♂️.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙ Configuration")
    selected_model = st.selectbox("Choose Model", ["deepseek-r1-distill-llama-70b"], index=0)
    language = st.selectbox("Select Response Language", ["English", "Hindi"])

    st.markdown("## SehaatSaathi Capabilities🤷‍♂️")
    st.markdown("""
    - 🤖 Your AI Doctor
    - 🧑‍⚕️ AI Health Assistant
    - 🔬 Symptom Analysis
    - 💊 Medicine Suggestions
    - 🏥 Health Advice
    - 🩺 Disease Diagnosis
    """)
    st.markdown("👨‍💻 Developer: Abhishek ❤️ Yadav")

# Initialize AI Model
ai_doctor = ChatGroq(api_key=groq_api_key, model=selected_model, temperature=0.3)

system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an AI Doctor named SehaatSaathi. Provide concise, specific medical advice based on symptoms, recommend medicines briefly, and always suggest consulting a real doctor for serious issues. Avoid unnecessary elaboration or thinking responses."
)

recognizer = sr.Recognizer()

def speak_text(text, lang="en"):
    tts = gTTS(text=text, lang=lang, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        tts.save(temp_audio.name)
        temp_audio_path = temp_audio.name
    with open(temp_audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
    os.remove(temp_audio_path)
    audio_html = f'<audio autoplay="true" controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

if "message_log" not in st.session_state:
    st.session_state.message_log = [{
        "role": "ai",
        "content": "Hello! I am your SehaatSaathi AI Doctor. How can I help you today? 🤖💉"
    }]

chat_container = st.container()

col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.chat_input("Describe your symptoms or ask about a medicine... 🤒💊")

with chat_container:
    for i, message in enumerate(st.session_state.message_log):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "ai":
                if st.button(f"🔊 Speak Response {i+1}", key=f"button_{i}"):
                    speak_text(message["content"], lang="hi" if language == "Hindi" else "en")

if user_query:
    st.session_state.message_log.append({"role": "user", "content": user_query})
    with st.spinner("🧠 AI Doctor Processing..."):
        prompt_chain = ChatPromptTemplate.from_messages([system_prompt] + [
            HumanMessagePromptTemplate.from_template(msg["content"]) if msg["role"] == "user" else AIMessagePromptTemplate.from_template(msg["content"])
            for msg in st.session_state.message_log
        ])
        processing_pipeline = prompt_chain | ai_doctor | StrOutputParser()
        full_response = processing_pipeline.invoke({})

        st.session_state.message_log.append({"role": "ai", "content": full_response})
        speak_text(full_response, lang="hi" if language == "Hindi" else "en")

    st.rerun()
