#!/bin/bash
set -e

MODE=${1:-production}

echo "Starting server in $MODE mode..."

# Common: Run migrations
echo "Running database migrations..."
python manage.py migrate --no-input

# Common: Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Mode-specific server startup
case $MODE in
  development|prod)
    echo "Starting Gunicorn server..."
    exec gunicorn -c gunicorn_prod.py WirdBackend.wsgi:application
    ;;

  development|dev)
    echo "Starting Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
    ;;

  *)
    echo "Error: Unknown mode '$MODE'. Use 'production' or 'development'"
    exit 1
    ;;
esac
