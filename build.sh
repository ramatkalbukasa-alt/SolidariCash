#!/usr/bin/env bash
set -o errexit

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Running migrations..."
python manage.py migrate --no-input

echo "==> Creating default admin account..."
python manage.py create_admin

echo "==> Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "==> Build complete."
