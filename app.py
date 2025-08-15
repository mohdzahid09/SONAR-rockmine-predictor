import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import streamlit as st
import pyttsx3
import threading

# Voice Engine Initialization
def init_voice_engine():
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        return engine
    except Exception as e:
        st.error(f"Voice initialization failed: {str(e)}")
        return None

engine = init_voice_engine()

# Voice Thread Manager
class VoiceThreadManager:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None

    def speak_continuously(self, text):
        while not self.stop_event.is_set() and engine:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                st.error(f"Error during speech: {str(e)}")
                break

    def start_speaking(self, text, continuous=False):
        self.stop_speaking()
        self.stop_event.clear()
        if continuous:
            self.thread = threading.Thread(target=self.speak_continuously, args=(text,), daemon=True)
            self.thread.start()
        else:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                st.error(f"Error during speech: {str(e)}")

    def stop_speaking(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()

voice_manager = VoiceThreadManager()

# Custom CSS for Enhanced UI
def inject_custom_css():
    st.markdown("""
    <style>
        body, h1, h2, h3, h4, h5, h6, p, div, span {
            color: white !important;
        }
        .main {
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d) !important;
        }
        .title {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px #000000;
            color: white !important;
        }
        .result-box {
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: white !important;
        }
        .rock-box { background: linear-gradient(135deg, #1D976C, #93F9B9); }
        .mine-box { background: linear-gradient(135deg, #ED213A, #93291E); animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    </style>
    """, unsafe_allow_html=True)

# Load the Model
@st.cache_resource
def load_model():
    try:
        data = pd.read_csv('Copy of sonar data.csv', header=None)
        X = data.drop(columns=60, axis=1)
        y = data[60]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, stratify=y, random_state=1)
        model = LogisticRegression()
        model.fit(X_train, y_train)
        return model
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

model = load_model()
inject_custom_css()
st.markdown('<h1 class="title">🎯 SONAR Rock or Mine Detector</h1>', unsafe_allow_html=True)

input_data = st.text_input('SONAR Signal :')

if st.button('Detect Object'):
    voice_manager.stop_speaking()  # Stop any ongoing speech
    try:
        values = np.array(input_data.split(','), dtype=float)
        if len(values) == 60:
            prediction = model.predict(values.reshape(1, -1))[0]
            if prediction == 'R':
                st.markdown('<div class="result-box rock-box">The Object is ROCK</div>', unsafe_allow_html=True)
                voice_manager.start_speaking("The Object is rock")
            else:
                st.markdown('<div class="result-box mine-box">WARNING! It\'s a MINE</div>', unsafe_allow_html=True)
                voice_manager.start_speaking("WARNING It's a Mine", continuous=True)
        else:
            st.error("Please enter exactly 60 numeric values.")
    except ValueError:
        st.error("Invalid input.")

if st.button('Stop Alert'):
    voice_manager.stop_speaking()
    st.success("Alert stopped.")

