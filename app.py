import streamlit as st
from streamlit_chat import message
import speech_recognition as sr
from gtts import gTTS
import os
import requests
import tempfile
from pathlib import Path
import time

class VoiceBot:
    def __init__(self):
        self.api_key = "qUpn0MpfhwXIMGl2AdCN4CV9L2fIfWc4"
        self.model_name = "mistral-small-latest"
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.persona = """I am Pavan Teja, an Artificial Intelligence and Machine Learning specialist."""

        self.responses = {
            "life story": """I'm **Pavan Teja**, an AI/ML specialist from Vizag...""",
            "superpower": """My core strength lies in **transforming complex AI concepts into practical solutions**...""",
            "grow": """As a tech professional, my top growth areas are: Public Speaking, Team Leadership, Product Architecture...""",
            "misconception": """People think I’m always serious, but I love humor and collaboration...""",
            "push limits": """I join hackathons and constantly experiment with new AI ideas..."""
        }

        self.conversation = []

    def get_response(self, question):
        question_lower = question.lower()
        for key, response in self.responses.items():
            if key in question_lower:
                return response.strip()

        messages = [{"role": "system", "content": self.persona}]
        messages.extend(self.conversation[-6:])
        messages.append({"role": "user", "content": f"Answer in 5-15 lines: {question}"})

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"model": self.model_name, "messages": messages}
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            self.conversation.append({"role": "user", "content": question})
            self.conversation.append({"role": "assistant", "content": content})
            return content
        except requests.exceptions.ConnectionError:
            st.error("Network error. Please check your internet connection.")
            return None
        except Exception as e:
            return f"Error: {str(e)}"

def listen_to_mic():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... (speak within 5 seconds)")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            return audio
    except sr.WaitTimeoutError:
        st.warning("⌛ No speech detected within timeout")
        return None
    except Exception as e:
        st.error(f"🔴 Error accessing microphone: {str(e)}")
        return None

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Audio Error: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="AI Voice BOT", page_icon="🤖", layout="wide")

    if 'bot' not in st.session_state:
        st.session_state.bot = VoiceBot()
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    if 'last_audio_file' not in st.session_state:
        st.session_state.last_audio_file = None

    st.markdown("""
    # 🎤 AI Voice BOT
    ## Using Mistral AI for Conversational AI
    """)

    chat_container = st.container()

    with chat_container:
        for i, msg in enumerate(st.session_state.bot.conversation):
            if msg["role"] == "user":
                message(msg["content"], is_user=True, key=f"msg_{i}")
            else:
                message(msg["content"], is_user=False, key=f"msg_{i}")

    col1, col2 = st.columns([3, 1])

    with col1:
        user_input = st.text_input("Type your question here", key="text_input")

        if st.button("🎤 Voice Input", use_container_width=True):
            audio = listen_to_mic()
            if audio:
                try:
                    recognizer = sr.Recognizer()
                    question = recognizer.recognize_google(audio)
                    st.session_state.text_input = question
                    user_input = question
                except sr.UnknownValueError:
                    st.error("Could not understand audio")
                except sr.RequestError:
                    st.error("Could not process audio")

        if user_input:
            with st.spinner('Processing your question...'):
                response = st.session_state.bot.get_response(user_input)
                st.markdown(response)
                audio_file = text_to_speech(response)
                if audio_file:
                    st.session_state.last_audio_file = audio_file
                    st.session_state.is_playing = True

    if st.session_state.is_playing and st.session_state.last_audio_file:
        st.audio(st.session_state.last_audio_file, format='audio/mp3')

    with col2:
        if st.button("🛑 Stop Audio", use_container_width=True):
            st.session_state.is_playing = False
            st.session_state.last_audio_file = None
            st.info("Audio stopped.")

if __name__ == "__main__":
    main()
