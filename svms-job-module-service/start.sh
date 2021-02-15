#!/bin/sh
# python manage.py makemigrations 
python manage.py migrate
#  python manage.py makemigrations job_catalog
#  python manage.py makemigrations job
#  python manage.py makemigrations job_distribution
#  python manage.py makemigrations onboarding
#  python manage.py makemigrations job
#  python manage.py makemigrations rate_card
#  python manage.py makemigrations submissions
#  python manage.py makemigrations offers
# python manage.py makemigrations interviews
#  python manage.py migrate
# python manage.py loaddata fixtures/*.json
python manage.py collectstatic --noinput
#python manage.py runserver 0.0.0.0:8002
ulimit -n 2048
service ssh start
#gunicorn simplify_job.wsgi:application --bind 0.0.0.0:8002 --workers 8 --threads 2 --worker-class gevent --timeout 20000
gunicorn simplify_job.asgi:application --bind 0.0.0.0:8002 --workers 4 --threads 2 --backlog 128 -k uvicorn.workers.UvicornWorker --log-level debug



exec "$@"
