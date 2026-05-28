#!/bin/sh

# Exit immediately if any command returns a non-zero status code
set -e

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server binding to 0.0.0.0:8000
echo "Starting Gunicorn web server..."
exec gunicorn ai_resume_analyzer.wsgi:application --bind 0.0.0.0:8000
