#!/bin/sh

# Wait for PostgreSQL
echo "Waiting for postgres..."

until nc -z postgres 5432; do
  sleep 1
done

# Go to the app directory
cd /usr/src/app

# Set Python output to unbuffered
export PYTHONUNBUFFERED=1

# Apply migrations
su -m myuser -c "python manage.py makemigrations formulavis"
su -m myuser -c "python manage.py migrate"

# Start the Django development server explicitly binding to all interfaces (0.0.0.0)
su -m myuser -c "python manage.py runserver 0.0.0.0:8000"

# Create a superuser with specified credentials
# su -m myuser -c "
#   DJANGO_SUPERUSER_PASSWORD=admin_formulavis \
#   python manage.py createsuperuser \
#     --noinput \
#     --username admin_formulavis \
#     --email patrykpiecuch3@gmail.com
# "


