import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Crée une instance de Celery
app = Celery('myproject')

# Utilise les settings de Django + namespace CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover les tâches dans tous les fichiers tasks.py
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
