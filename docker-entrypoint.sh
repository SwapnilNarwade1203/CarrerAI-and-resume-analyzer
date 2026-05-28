#!/bin/sh

# Exit immediately if any command returns a non-zero status code
set -e

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Populate default database tables automatically on startup
echo "Seeding default data (skills, roles, questions)..."
python manage.py populate_initial_data
python manage.py import_aptitude_questions
python manage.py import_skill_questions
python manage.py seed_company_questions

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server binding to 0.0.0.0:8000
echo "Starting Gunicorn web server..."
exec gunicorn ai_resume_analyzer.wsgi:application --bind 0.0.0.0:8000
