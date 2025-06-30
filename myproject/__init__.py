# Ceci permet de lancer celery automatiquement avec Django
from .celery import app as celery_app # type: ignore

__all__ = ('celery_app',)
