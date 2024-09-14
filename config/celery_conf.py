from celery import Celery
from django.db.transaction import set_autocommit

app = Celery("counter-validation-tool")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

set_autocommit(True)
