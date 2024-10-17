import os
import time
import urllib.parse

import celery
import requests
from celery.contrib.django.task import DjangoTask
from django.conf import settings
from django.db import transaction

from core.classes.registry import RegistrySync
from core.models import Validation


class ValidationTask(DjangoTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        obj = Validation.objects.get(pk=args[0])
        obj.status = Validation.StatusEnum.FAILURE
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
    obj = Validation.objects.get(pk=pk)
    obj.status = Validation.StatusEnum.RUNNING
    obj.save()
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
    obj.result = json["result"]
    obj.memory = json["memory"]
    obj.time = end - start
    obj.status = Validation.StatusEnum.SUCCESS
    obj.save()


@celery.shared_task(base=ValidationTask)
def validate_sushi(pk, credentials: dict):
    obj = Validation.objects.get(pk=pk)
    obj.status = Validation.StatusEnum.RUNNING
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
    obj.result = json["result"]
    obj.status = Validation.StatusEnum.SUCCESS
    obj.save()
