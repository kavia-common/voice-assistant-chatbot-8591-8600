# Backend Dependencies and Preview Notes

Python: Requires Python 3.12.x (container default).

Install:
- pip install -r requirements.txt

Why pins:
- Django 5.0.6: compatible with Python 3.12; keeps features modern without hitting Django 5.1/5.2 changes.
- drf-yasg 1.21.7: stable with DRF 3.15.x and Django 5.0.x.
- SpeechRecognition 3.10.3: pure-Python; no pyaudio required (we use file upload input).
- gTTS 2.5.4: latest available on PyPI at time of writing; 2.6.0 does not exist, which caused previous install failures.
- pyttsx3 2.98: pure-Python; may rely on system audio backends at runtime; our code already falls back to gTTS if it fails.

Avoided by default:
- pocketsphinx: heavy system build; optional/off by default (STT falls back to Google Web Speech).
- pyaudio, opencv, webrtcvad: system headers/wheels often missing in preview containers.

Run:
- python manage.py migrate
- python manage.py runserver 0.0.0.0:3001

Swagger:
- /docs
