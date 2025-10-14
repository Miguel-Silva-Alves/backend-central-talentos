#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    echo $SQL_HOST
    echo $SQL_PORT

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

#python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate

DJANGO_SUPERUSER_USERNAME=testuserr \
DJANGO_SUPERUSER_PASSWORD=testpasss \
DJANGO_SUPERUSER_EMAIL="adminn@admin.com" \
python manage.py createsuperuser --noinput


# DJANGO_SUPERUSER_USERNAME=gabriel \
# DJANGO_SUPERUSER_PASSWORD=gabriel \
# DJANGO_SUPERUSER_EMAIL="gabriel@admin.com" \
# python manage.py createsuperuser --noinput

exec "$@"