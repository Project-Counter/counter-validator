import os
import time
import urllib.parse

import celery
import requests
from celery.contrib.django.task import DjangoTask
from counter.classes.registry import RegistrySync
from django.conf import settings
from django.db import transaction
from validations.enums import ValidationStatus
from validations.models import Validation


class ValidationTask(DjangoTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        obj = Validation.objects.get(pk=args[0])
        obj.status = ValidationStatus.FAILURE
        obj.save()


@celery.shared_task
@transaction.atomic
def update_registry_models(cls=None):
    if cls is None:
        cls = RegistrySync()
    cls.sync()


@celery.shared_task(base=ValidationTask)
def validate_file(pk):
    start = time.monotonic()
    obj = Validation.objects.select_related("core").get(pk=pk)
    obj.core.status = ValidationStatus.RUNNING
    obj.core.save()
    # time.sleep(5)

    with obj.file.open("rb") as fp:
        req = requests.post(
            settings.CTOOLS_URL + "file.php",
            params={"extension": os.path.splitext(obj.filename)[1].lstrip(".")},
            data=fp,
        )
    req.raise_for_status()

    end = time.monotonic()
    json = req.json()
    obj.result_data = json["result"]
    obj.core.used_memory = json["memory"]
    obj.core.duration = end - start
    obj.core.status = ValidationStatus.SUCCESS
    obj.core.save()
    obj.save()


@celery.shared_task(base=ValidationTask)
def validate_sushi(pk, credentials: dict):
    obj = Validation.objects.get(pk=pk)
    obj.status = ValidationStatus.RUNNING
    obj.save()

    url = credentials.pop("url")
    credentials["begin_date"] = "2024-07-01"
    credentials["end_date"] = "2024-07-31"
    credentials = {k: v for k, v in credentials.items() if v}
    req = requests.post(
        settings.CTOOLS_URL + "sushi.php",
        params={"url": url + "?" + urllib.parse.urlencode(credentials)},
    )
    req.raise_for_status()

    json = req.json()
    obj.result_data = json["result"]
    obj.status = ValidationStatus.SUCCESS
    obj.save()
