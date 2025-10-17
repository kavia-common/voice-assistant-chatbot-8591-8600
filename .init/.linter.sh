#!/usr/bin/env bash
set -euo pipefail

# Run flake8 via python -m to avoid PATH issues in CI/preview
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python interpreter not found."
  exit 1
fi

# If flake8 is not installed in the environment, print guidance and exit gracefully (non-fatal)
set +e
$PY -m flake8 --version >/dev/null 2>&1
FLK_STATUS=$?
set -e

if [ $FLK_STATUS -ne 0 ]; then
  echo "flake8 is not installed in the current environment. Skipping lint step."
  exit 0
fi

# Lint only the backend service code
$PY -m flake8 voice-assistant-chatbot-8591-8600/voice_chatbot_backend --max-line-length=120
echo "Lint passed."
