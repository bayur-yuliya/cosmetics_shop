#!/bin/bash
set -e

if [[ "$*" == *"gunicorn"* ]] || [[ "$*" == *"runserver"* ]]; then
    echo "Applying migrations..."
    python manage.py migrate --noinput

    echo "Collecting static..."
    python manage.py collectstatic --noinput

    echo "Running custom commands..."
    python manage.py translation_perms
    python manage.py create_groups
    python manage.py create_info
    python manage.py add_superuser_perm
fi

exec "$@"