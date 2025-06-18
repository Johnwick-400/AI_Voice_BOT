import streamlit as st
from streamlit_chat import message
import speech_recognition as sr
import pyttsx3
import requests
from config import API_KEY, MODEL_NAME, API_URL

class VoiceBot:
    def __init__(self):
        self.api_key = API_KEY
        self.model_name = MODEL_NAME
        self.api_url = API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.persona = """You are Pavan Teja, a 24-year-old male AI/ML specialist from Vizag. 
        Always respond in first person as Pavan. When someone asks who you are, 
        introduce yourself as Pavan Teja, never mention being an AI model."""
        self.conversation = []

    def get_response(self, question):
        messages = [{"role": "system", "content": self.persona}]
        messages.extend(self.conversation[-6:])
        messages.append({"role": "user", "content": question})

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"model": self.model_name, "messages": messages}
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]
            self.conversation.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            return f"Error: {str(e)}"

def init_session_state():
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False

def speak_text(text):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if "male" in voice.name.lower() or "english-us" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 170)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Speech Error: {str(e)}")

def main():
    st.set_page_config(page_title="AI Voice BOT", page_icon="🎤", layout="wide")

    init_session_state()

    if 'bot' not in st.session_state:
        st.session_state.bot = VoiceBot()

    st.title("🎤 AI Voice BOT")
    st.subheader("Using Mistral AI for Conversational AI")

    for i, msg in enumerate(st.session_state.bot.conversation):
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=f"user_{i}")
        else:
            message(msg["content"], is_user=False, key=f"bot_{i}")

    if st.button("🎙️ Start Voice Input", use_container_width=True):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                st.info("🎧 Listening... (Speak now)")
                audio = recognizer.listen(source, timeout=5)
                question = recognizer.recognize_google(audio)
                st.write("🧑 You said:", question)

                st.session_state.bot.conversation.append({"role": "user", "content": question})
                with st.spinner('💬 Generating response...'):
                    response = st.session_state.bot.get_response(question)
                    st.session_state.bot.conversation.append({"role": "assistant", "content": response})
                    st.markdown(response)
                    speak_text(response)

        except sr.UnknownValueError:
            st.error("Sorry, I couldn’t understand what you said.")
        except sr.RequestError:
            st.error("Speech Recognition service unavailable.")
        except Exception as e:
            st.error(f"Unexpected Error: {str(e)}")

if __name__ == "__main__":
    main()
