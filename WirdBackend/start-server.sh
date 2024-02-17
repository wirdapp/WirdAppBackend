#!/bin/bash

export DJANGO_SETTINGS_MODULE="WirdBackend.settings.settings"
python manage.py migrate --no-input
gunicorn -c gunicorn_prod.py
