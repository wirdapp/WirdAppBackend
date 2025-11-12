#!/bin/bash
set -e


DB_HOST=${DATABASE_HOST:-127.0.0.1}
DB_PORT=${DATABASE_PORT:-5432}
WAIT_TIMEOUT=${WAIT_TIMEOUT:-60}

echo "Waiting for database ${DB_HOST}:${DB_PORT} (timeout ${WAIT_TIMEOUT}s)..."
counter=0
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  counter=$((counter+1))
  if [ "$counter" -ge "$WAIT_TIMEOUT" ]; then
    echo "Timed out waiting for ${DB_HOST}:${DB_PORT}"
    exit 1
  fi
  sleep 1
done
echo "Database is up."

MODE=${1:-production}

echo "Starting server in $MODE mode..."

if [ "${ENABLE_GUI:-}" = "true" ] || [ "${ENABLE_ADMIN:-}" = "true" ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --no-input
fi
# Common: Run migrations
echo "Running database migrations..."
python manage.py migrate --no-input

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
