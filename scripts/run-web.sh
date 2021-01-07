#!/bin/sh
# pipenv run python scripts/wait-for-postgres.py
pipenv run python manage.py migrate
pipenv run python manage.py runserver 0.0.0.0:8000