import streamlit as st
from streamlit_chat import message
import speech_recognition as sr
from gtts import gTTS
import os
import requests
import tempfile
import pygame
from pathlib import Path
import time

pygame.mixer.init()

class VoiceBot:
    def __init__(self):
        self.api_key = "qUpn0MpfhwXIMGl2AdCN4CV9L2fIfWc4"
        self.model_name = "mistral-small-latest"
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Updated persona to always respond as Pavan
        self.persona = """You are Pavan Teja, a 24-year-old male AI/Machine Learning specialist from Vizag. 
        Always respond in first person as Pavan. When someone asks who you are, 
        introduce yourself as Pavan Teja, never mention being an AI model."""
        
        # Updated default responses
        self.responses = {
            "who are you": """Hi! I'm Pavan Teja, an AI and Machine Learning specialist from Vizag. 
            I specialize in building production-grade AI systems and currently work as an AI/ML Engineer at Hiringhood.""",
            
            "superpower": """
# Technical Expertise 💪

My core strength lies in **transforming complex AI concepts into practical solutions**. 

- 🔧 Convert ideas into production-ready AI applications
- 🚀 Developed enterprise-level ML systems
- 🌉 Bridge theoretical concepts with real-world implementation
            """,
            
            "grow": """
# Growth Focus 📈

As a male professional in tech, my top growth areas are:

1. **Public Speaking** 🎤
   - Mastering technical presentations
   - Developing executive communication skills

2. **Team Leadership** 👥
   - Leading technical teams effectively
   - Scaling project management capabilities

3. **Product Architecture** 💡
   - System design optimization
   - Enterprise solution architecture
            """,
            
            "misconception": """
# Breaking Stereotypes 🤔

As a male engineer focused on AI:

- 💡 Known for technical depth but equally value creativity
- 🎯 Balance precision with innovation
- 🤝 Foster collaborative problem-solving
- 🚀 Drive results while maintaining team spirit
            """,
            
            "push limits": """
# Innovation Drive 🚀

Constantly pushing technical boundaries:

- 🏆 Leading hackathon teams
- 💡 Pioneering AI solutions
- 🔬 Advancing LLM applications
- 📚 Building next-gen AI systems
            """
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
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            st.error("Network error. Please check your internet connection.")
            return None
        except Exception as e:
            return f"Error: {str(e)}"

def stop_audio():
    if hasattr(st.session_state, 'current_audio_file'):
        pygame.mixer.music.stop()
        try:
            os.remove(st.session_state.current_audio_file)
        except:
            pass
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
        return None
    except Exception as e:
        st.error(f"🔴 Error accessing microphone: {str(e)}")
        return None

def text_to_speech_and_play(text):
    try:
        tts = gTTS(text=text, lang='en', tld='co.in')  # Using Indian English voice
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            pygame.mixer.music.load(fp.name)
            pygame.mixer.music.play()
            st.session_state.current_audio_file = fp.name
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
        if st.button("🎤 Start Voice Input", use_container_width=True):
            audio = listen_to_mic()
            if audio:
                try:
                    recognizer = sr.Recognizer()
                    question = recognizer.recognize_google(audio)
                    st.write("You said:", question)
                    
                    # Add user message to conversation
                    st.session_state.bot.conversation.append({"role": "user", "content": question})
                    
                    # Get and process response
                    with st.spinner('Processing your question...'):
                        response = st.session_state.bot.get_response(question)
                        if response:
                            # Add bot response to conversation
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
