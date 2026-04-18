#!/usr/bin/env bash
set -o errexit

# Build process - Fixed all import issues in views
pip install -r requirements.txt
python manage.py collectstatic --noinput
