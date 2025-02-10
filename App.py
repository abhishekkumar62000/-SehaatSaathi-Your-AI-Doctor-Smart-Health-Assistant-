import os
import streamlit as st
import speech_recognition as sr
import tempfile
from gtts import gTTS
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import SystemMessagePromptTemplate
import base64
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

st.set_page_config("🤖SehaatSaathi-Your AI Doctor😷", page_icon="🧠", layout="wide")

st.title("🤖SehaatSaathi - AI Doctor Assistant🧑‍⚕️")
st.caption("🚀 Instant Medical Advice & Medicine Recommendations.")

with st.sidebar:
    st.header("⚙ Configuration")
    selected_model = st.selectbox("Choose Model", ["deepseek-r1-distill-llama-70b"], index=0)
    language = st.selectbox("Select Response Language", ["English", "Hindi"])

    st.markdown("## SehaatSaathi Capabilities🤷‍♂️")
    st.markdown("""
    - 🤖 AI Doctor
    - 🧑‍⚕️ Health Assistant
    - 🔬 Symptom Analysis
    - 💊 Medicine Suggestions
    - 🏥 Health Advice
    """)
    st.markdown("👨‍💻 Developer: Abhishek ❤️ Yadav")

ai_doctor = ChatGroq(api_key=groq_api_key, model=selected_model, temperature=0.3)

recognizer = sr.Recognizer()

def speak_text(text, lang="en"):
    if not isinstance(text, str) or not text.strip():
        return  # Avoid speaking empty or invalid responses
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

def recognize_speech():
    try:
        if not sr.Microphone.list_microphone_names():
            return "❌ No microphone detected!"
        with sr.Microphone() as source:
            st.info("🎤 Speak now...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
    except sr.UnknownValueError:
        return "❌ Could not understand your voice."
    except sr.RequestError:
        return "❌ Speech service unavailable."
    except OSError:
        return "❌ No microphone found!"

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        text = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
        return text.strip() if text.strip() else "❌ No text found in PDF."
    except Exception:
        return "❌ Error processing PDF."

def extract_text_from_image(image_file):
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text.strip() if text.strip() else "❌ No text detected."
    except Exception:
        return "❌ Error processing image."

if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! I am your AI Doctor. How can I help? 🤖💉"}]

chat_container = st.container()

col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.chat_input("Describe your symptoms... 🤒💊")
with col2:
    if st.button("🎙️ Speak Symptoms"):
        user_query = recognize_speech()
        st.text(f"🗣️ You Said: {user_query}")

if user_query:
    with st.spinner("🧠 AI Doctor Thinking..."):
        ai_response = ai_doctor.invoke(user_query)
        if hasattr(ai_response, "content"):
            ai_response = ai_response.content.strip()
        st.session_state.message_log.append({"role": "ai", "content": ai_response})
        st.chat_message("ai").markdown(ai_response)
        speak_text(ai_response, lang="hi" if language == "Hindi" else "en")

uploaded_file = st.file_uploader("📤 Upload Medical Report (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])
if uploaded_file:
    report_text = extract_text_from_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else extract_text_from_image(uploaded_file)
    st.write("📄 Extracted Text:", report_text)
    if report_text:
        with st.spinner("🔬 Analyzing Medical Report..."):
            report_analysis = ai_doctor.invoke(f"Analyze this report: {report_text}")
            if hasattr(report_analysis, "content"):
                report_analysis = report_analysis.content.strip()
            st.write("💊 AI Analysis:", report_analysis)
            speak_text(report_analysis, lang="hi" if language == "Hindi" else "en")
