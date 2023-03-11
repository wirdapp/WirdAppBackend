#!/usr/bin/env bash

set -ex

python manage.py migrate
gunicorn WirdBackend.wsgi -c ./gunicorn/prod.py -b 0.0.0.0:8000
