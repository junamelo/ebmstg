"""Tâches asynchrones de facturation.

Les traitements PDF seront déplacés ici progressivement afin que les requêtes
HTTP ne restent pas bloquées pendant le découpage.
"""

from uuid import uuid4

from celery import shared_task
from django.core.cache import cache


@shared_task(name='billing.verifier_garnet')
def verifier_garnet():
    """Tâche non métier servant à valider Garnet + Celery de bout en bout."""
    key = f'celery-health:{uuid4()}'
    cache.set(key, 'ok', timeout=60)
    return {
        'broker': 'Garnet',
        'cache_roundtrip': cache.get(key) == 'ok',
    }
