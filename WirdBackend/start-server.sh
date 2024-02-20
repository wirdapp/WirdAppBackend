#!/bin/bash

python manage.py migrate --no-input
gunicorn -c gunicorn_prod.py WirdBackend.wsgi:application
