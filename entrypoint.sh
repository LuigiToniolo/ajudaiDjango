#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

git config --global --add safe.directory /usr/src/app

set -o errexit

#python manage.py collectstatic --no-input
python manage.py migrate

exec "$@"
