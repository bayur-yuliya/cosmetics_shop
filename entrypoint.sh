#!/bin/bash
set -e

# Мы в /app/src
echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput

# Проверка/создание медиа-директорий на случай, если volume пустой
mkdir -p /app/media/default /app/media/product_images

echo "Running custom commands..."
python manage.py translation_perms
python manage.py create_groups
python manage.py create_info
python manage.py add_superuser_perm

exec "$@"