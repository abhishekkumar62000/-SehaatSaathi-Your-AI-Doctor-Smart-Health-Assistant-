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
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import pyaudio

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
    "You are an AI Doctor named SehaatSaathi. Provide medical advice based on symptoms, recommend medicines, and always suggest consulting a real doctor for serious issues."
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

# Feature 1: Voice Input (Speech-to-Text) - Fixed

def recognize_speech():
    try:
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            return "❌ No microphone detected! Check your device settings."
        with sr.Microphone() as source:
            st.info("🎤 Speak now...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            return text
    except sr.UnknownValueError:
        return "❌ Sorry, couldn't recognize your voice!"
    except sr.RequestError:
        return "❌ Speech service unavailable!"
    except OSError:
        return "❌ No microphone found! Check your settings."

# Feature 2: Medical Report Analysis (PDF/Image OCR) - Fixed

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        text = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
        return text.strip() if text.strip() else "❌ No text found in PDF."
    except Exception:
        return "❌ Error processing PDF. Ensure it's not a scanned document."

def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text.strip() if text.strip() else "❌ No text detected in image."
    except Exception:
        return "❌ Error processing image. Ensure it's clear."

if "message_log" not in st.session_state:
    st.session_state.message_log = [{
        "role": "ai",
        "content": "Hello! I am your SehaatSaathi AI Doctor. How can I help you today? 🤖💉",
        "think": None
    }]

chat_container = st.container()

col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.chat_input("Describe your symptoms or ask about a medicine... 🤒💊")

with col2:
    if st.button("🎙️ Speak Symptoms"):
        user_query = recognize_speech()
        st.text(f"🗣️ You Said: {user_query}")

with chat_container:
    for i, message in enumerate(st.session_state.message_log):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "ai":
                if st.button(f"🔊 Speak Response {i+1}", key=f"button_{i}"):
                    speak_text(message["content"], lang="hi" if language == "Hindi" else "en")

if user_query:
    st.session_state.message_log.append({"role": "user", "content": user_query, "think": None})
    with st.spinner("🧠 AI Doctor Thinking..."):
        prompt_chain = ChatPromptTemplate.from_messages([system_prompt] + [
            HumanMessagePromptTemplate.from_template(msg["content"]) if msg["role"] == "user" else AIMessagePromptTemplate.from_template(msg["content"])
            for msg in st.session_state.message_log
        ])
        processing_pipeline = prompt_chain | ai_doctor | StrOutputParser()
        full_response = "".join(processing_pipeline.stream({}))
        st.session_state.message_log.append({"role": "ai", "content": full_response})
        speak_text(full_response, lang="hi" if language == "Hindi" else "en")
    st.rerun()

# Feature 3: Emergency Contact Button

def emergency_contact():
    st.warning("🚨 In case of a medical emergency, call:")
    st.write("📞 **Ambulance:** 108")
    st.write("🏥 **Nearest Hospital:** Check Google Maps")
    st.write("[🔍 Find Nearby Hospitals](https://www.google.com/maps/search/nearest+hospital/)")

if st.sidebar.button("🚑 Emergency Contact"):
    emergency_contact()

uploaded_file = st.file_uploader("📤 Upload Medical Report (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])
if uploaded_file:
    report_text = extract_text_from_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else extract_text_from_image(uploaded_file)
    st.write("📄 Extracted Text:", report_text)
