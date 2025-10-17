# voice-assistant-chatbot-8591-8600

Backend: Django REST API for STT, Chat, and TTS.

How to run (development):
- Install Python 3.10+ and virtualenv.
- cd voice-assistant-chatbot-8591-8600/voice_chatbot_backend
- python -m venv venv && . venv/bin/activate
- pip install -r requirements.txt
- cp .env.example .env and update values as needed
- python manage.py migrate
- python manage.py runserver 0.0.0.0:3001

Swagger docs:
- Visit /docs at http://localhost:3001/docs

Endpoints (base /api):
- GET /api/health -> {"message": "Server is up!"}
- POST /api/stt (multipart/form-data)
  - form fields: file (required), language (optional)
  - returns: { "text": str, "engine": "google|pocketsphinx", "duration_ms": int }
- POST /api/chat (application/json)
  - body: { "text": str, "session_id"?: str }
  - returns: { "reply": str, "provider": "openai|heuristic" }
  - If OPENAI_API_KEY is set, OpenAI is used; otherwise heuristic NLU.
- POST /api/tts (application/json)
  - body: { "text": str, "voice"?: str, "engine"?: "pyttsx3|gtts" }
  - returns: audio bytes with the correct Content-Type and Content-Disposition.
    - pyttsx3 -> audio/wav download
    - gTTS -> audio/mpeg download

Environment variables (.env):
- DEBUG=True
- SECRET_KEY=change-me
- OPENAI_API_KEY=sk-...
- GOOGLE_APPLICATION_CREDENTIALS=/path/to/google/creds.json
- TTS_ENGINE=pyttsx3
- STT_PREFERRED_ENGINE=google

Notes:
- In container/preview environments, we avoid heavy system-level deps. We do not install pocketsphinx by default to keep builds reliable.
- STT uses SpeechRecognition and will prefer Google Web Speech API unless you explicitly set STT_PREFERRED_ENGINE=sphinx and install pocketsphinx.
- TTS uses pyttsx3 (offline) to generate WAV; falls back to gTTS (MP3) if needed. If system audio backends are unavailable, pyttsx3 may fail at runtime—code already falls back to gTTS.
- Chat uses OpenAI if configured; else a simple heuristic responder.