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

## Docker and build optimization

- Dockerfile uses multi-stage and installs dependencies before copying app code to maximize layer caching.
- pip cache mount accelerates repeated builds; apt caches are cleaned.
- No tests/migrations/collectstatic at build time; do these at runtime/CI if needed.
- requirements.lock (generated during build) documents resolved versions for deterministic rebuilds. You may choose to:
  - Continue installing from requirements.txt (default) for development convenience.
  - Or pin to requirements.lock for strict reproducibility:
    - Replace "pip install -r requirements.txt" with "pip install --no-deps -r requirements.lock" in Dockerfile or CI.

Note:
- Docker CMD runs gunicorn (config.wsgi) on port 3001. Ensure gunicorn is installed (added in requirements.txt).
- In DEBUG, ALLOWED_HOSTS is permissive. In production, set DJANGO_ALLOWED_HOSTS env (comma-separated).

## Troubleshooting dependency install on slim images

If `pip install -r requirements.txt` fails on a slim Python image:
- Ensure you are building with Python 3.12 (default in Dockerfile).
- We intentionally avoid OS-dependent audio packages (pyaudio, pocketsphinx, webrtcvad, torchaudio, opencv). Do not add them unless you extend the Dockerfile with the needed system libs.
- If you must enable pocketsphinx (offline STT), add it explicitly and extend Dockerfile to install required system libraries. Otherwise leave it disabled and use the default Google Web Speech fallback.
- If you see errors related to building wheels or compiling extensions, confirm that the build stage includes:
  - build-essential
  - libffi-dev
These are already present in the Dockerfile’s deps stage.

If you still hit installation issues, try:
- Clearing pip caches and rebuilding: `docker build --no-cache ...`
- Switching to the pinned lock for strict reproducibility:
  - Replace the deps installation line with `pip install --no-deps -r /app/requirements.lock` after generating it once successfully.

Known good pins:
- Django==5.0.6
- djangorestframework==3.15.2
- drf-yasg==1.21.7
- SpeechRecognition==3.10.3
- gTTS==2.5.4
- pyttsx3==2.98
- gunicorn==22.0.0

Optional heavy/OS-dependent packages (not installed by default):
- pocketsphinx (offline STT)
- pyaudio/portaudio
- webrtcvad
- torchaudio/torch
- opencv-python
