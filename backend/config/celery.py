import os
from celery import Celery

# Set default settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("nexova")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover task modules from all registered Django app configs
app.autodiscover_tasks()
