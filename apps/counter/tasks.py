import celery
from django.db import transaction

from counter.classes.registry import RegistrySync


@celery.shared_task
@transaction.atomic
def update_registry_models(cls=None):
    if cls is None:
        cls = RegistrySync()
    cls.sync()
