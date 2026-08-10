"""Configuration Celery utilisant Garnet (protocole RESP compatible Redis)."""

import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')

app = Celery('moov_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
