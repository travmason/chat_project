# chat_project/celery.py

import os
from celery import Celery

# Set default Django settings module for 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')

app = Celery('chat_project',
             broker_connection_retry_on_startup=True,
             )

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
