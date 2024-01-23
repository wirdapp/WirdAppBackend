#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
# python manage.py makemigrations
python manage.py migrate --no-input
# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
