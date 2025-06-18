# 🎤 AI VoiceBot – Streamlit + Mistral AI

This project is a voice-controlled chatbot named **Pavan Teja**, powered by [Mistral AI](https://mistral.ai). The bot can listen to your voice input, send it to the Mistral AI model for response, and read it aloud using text-to-speech.

> 💬 "You are Pavan Teja, a 24-year-old AI/ML specialist from Vizag. You always speak in first person."

---

## 🚀 Live Demo

You can try the deployed app at:  
👉 [[https://huggingface.co/spaces/Johnwick0007/voice_bot]]

---

## 📂 Project Structure

```

voicebot/
├── app.py            
├── config.py         # API Key configuration file
├── requirements.txt  # Required Python packages
└── README.md         # You're here!

````

---

## ✅ Features

- 🎙️ Voice input using your microphone
- 🤖 AI response generation using Mistral API
- 🔊 Speech output via `pyttsx3` (text-to-speech)
- 🧠 Maintains short-term memory of previous 6 messages

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Johnwick-400/AI_Voice_BOT
cd AI_Voice_BOT
````

### 2. Install Python Dependencies

Make sure you're using Python 3.10+

```bash
pip install -r requirements.txt
```

### 3. Add Your API Key

Open `config.py` and replace with your actual [Mistral API Key](https://console.mistral.ai):

```python
API_KEY = "your_actual_api_key"
```

---

## ▶️ Run the App Locally

```bash
streamlit run app.py
```

This will open the app in your browser at `http://localhost:8501`.

---

## 🧠 Example Use

1. Click **"🎙️ Start Voice Input"**
2. Speak into your microphone.
3. The bot will transcribe, generate a response, and speak it aloud.
4. Conversation history will appear in the chat interface.

---
