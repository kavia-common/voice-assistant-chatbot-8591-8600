#!/bin/bash
cd /home/kavia/workspace/code-generation/voice-assistant-chatbot-8591-8600/voice_chatbot_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

