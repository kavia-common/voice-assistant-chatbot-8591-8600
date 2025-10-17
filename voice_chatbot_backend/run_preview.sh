#!/usr/bin/env bash
set -euo pipefail

export PYTHONUNBUFFERED=1

python3 -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:3001
