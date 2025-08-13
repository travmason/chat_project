web: gunicorn --bind 0.0.0.0:8000 --workers=1 --threads=15 chat_project.wsgi:application
worker: celery -A chat_project worker --loglevel=info

