#!/bin/bash

set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Preparing media directories..."
mkdir -p /app/media/default

python manage.py translation_perms
python manage.py create_groups
python manage.py add_superuser_perm

exec "$@"