#!/usr/bin/env bash

set -ex

#python manage.py makemigrations
#python manage.py migrate
gunicorn Ramadan_Competition_Rest.wsgi -c ./gunicorn/prod.py -b 0.0.0.0:8000
