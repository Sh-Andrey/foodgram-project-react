#!/bin/sh
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py load_data
python manage.py loaddata data/tags.json
python manage.py createsuperuser