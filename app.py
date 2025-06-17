import streamlit as st
from streamlit_chat import message
import speech_recognition as sr
from gtts import gTTS
import os
import requests
import tempfile

class VoiceBot:
    def __init__(self):
        self.api_key = "qUpn0MpfhwXIMGl2AdCN4CV9L2fIfWc4"
        self.model_name = "mistral-small-latest"
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.persona = """You are Pavan Teja, a 24-year-old male AI/Machine Learning specialist from Vizag. 
        Always respond in first person as Pavan. When someone asks who you are, 
        introduce yourself as Pavan Teja, never mention being an AI model."""
        
        self.responses = {
            "who are you": "Hi! I'm Pavan Teja, an AI and Machine Learning specialist from Vizag...",
            "superpower": "# Technical Expertise 💪\n\nMy core strength lies in...",
            "grow": "# Growth Focus 📈\n\nAs a male professional in tech, my top growth areas are...",
            "misconception": "# Breaking Stereotypes 🤔\n\nAs a male engineer focused on AI...",
            "push limits": "# Innovation Drive 🚀\n\nConstantly pushing technical boundaries..."
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
            json_data = response.json()
            return json_data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            st.error(f"Network/API error: {e}")
        except Exception as e:
            st.error(f"Parsing error: {str(e)}")
        return "Sorry, something went wrong."

def stop_audio():
    if hasattr(st.session_state, 'current_audio_file'):
        try:
            os.remove(st.session_state.current_audio_file)
        except Exception as e:
            st.warning(f"Could not delete audio file: {e}")
        st.session_state.is_playing = False

def listen_to_mic():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... (speak within 5 seconds)")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            return audio
    except sr.WaitTimeoutError:
        st.warning("⌛ No speech detected within timeout")
    except Exception as e:
        st.error(f"🔴 Error accessing microphone: {str(e)}")
    return None

def text_to_speech_and_play(text):
    try:
        tts = gTTS(text=text, lang='en', tld='co.in')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            st.session_state.current_audio_file = fp.name
            return fp.name
    except Exception as e:
        st.error(f"Audio generation error: {str(e)}")
    return None

def main():
    st.set_page_config(page_title="AI Voice BOT", page_icon="🤖", layout="wide")

    if 'bot' not in st.session_state:
        st.session_state.bot = VoiceBot()
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False

    st.title("🎤 AI Voice BOT")
    st.subheader("Using Mistral AI for Conversational AI")

    chat_container = st.container()
    with chat_container:
        for i, msg in enumerate(st.session_state.bot.conversation):
            message(msg["content"], is_user=(msg["role"] == "user"), key=f"msg_{i}")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🎤 Start Voice Input", use_container_width=True):
            audio = listen_to_mic()
            if audio:
                try:
                    recognizer = sr.Recognizer()
                    question = recognizer.recognize_google(audio)
                    st.write("🗣️ You said:", question)

                    st.session_state.bot.conversation.append({"role": "user", "content": question})

                    with st.spinner('🤖 Generating response...'):
                        response = st.session_state.bot.get_response(question)
                        if response:
                            st.session_state.bot.conversation.append({"role": "assistant", "content": response})
                            st.markdown(response)

                            audio_file = text_to_speech_and_play(response)
                            if audio_file:
                                st.audio(audio_file, format='audio/mp3')
                                st.session_state.is_playing = True
                except sr.UnknownValueError:
                    st.error("Could not understand audio")
                except sr.RequestError:
                    st.error("Could not process audio")

    with col2:
        if st.button("🛑 Stop Audio", use_container_width=True):
            stop_audio()

if __name__ == "__main__":
    main()
