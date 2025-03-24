import base64
import logging
import os
import time
import uuid
import zlib

import celery
import requests
from celery.contrib.django.task import DjangoTask
from django.core.files.uploadedfile import SimpleUploadedFile

from validations.enums import ValidationStatus
from validations.hashing import checksum_bytes
from validations.models import CounterAPIValidation, Validation
from validations.validation_modules import (
    create_validation_module_lock,
    get_available_validation_module_url,
)

logger = logging.getLogger(__name__)


class ValidationTask(DjangoTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        obj = Validation.objects.get(pk=args[0])
        obj.status = ValidationStatus.FAILURE
        obj.save()


@celery.shared_task(base=ValidationTask)
def validate_file(pk: uuid.UUID):
    while not (vm_url := get_available_validation_module_url()):
        logger.info("No available validation module, waiting...")
        time.sleep(1)

    logger.info("Using validation module: %s", vm_url)

    obj = Validation.objects.select_related("core").get(pk=pk)
    obj.core.status = ValidationStatus.RUNNING
    obj.core.save()

    start = time.monotonic()
    lock = create_validation_module_lock(vm_url)
    lock.acquire(blocking=True)
    try:
        with obj.file.open("rb") as fp:
            req = requests.post(
                vm_url + "file.php",
                params={"extension": os.path.splitext(obj.filename)[1].lstrip(".")},
                data=fp,
            )
        req.raise_for_status()
    except Exception as e:
        obj.core.status = ValidationStatus.FAILURE
        obj.core.error_message = str(e)
        end = time.monotonic()
        obj.core.duration = end - start
        obj.core.save()
        obj.save()
        return
    finally:
        lock.release()

    json = req.json()
    logger.debug("Validation result: %s", json)
    obj.core.stats = obj.add_result(json.get("result", {}))
    obj.core.used_memory = json["memory"]
    obj.core.status = ValidationStatus.SUCCESS
    if header := json["result"].get("header"):
        # replace potentially null values with ""
        obj.core.cop_version = header.get("cop_version", "") or ""
        obj.core.report_code = header.get("report_id", "") or ""
    end = time.monotonic()
    obj.core.duration = end - start
    obj.core.save()
    obj.save()


@celery.shared_task(base=ValidationTask)
def validate_counter_api(pk):
    while not (vm_url := get_available_validation_module_url()):
        logger.info("No available validation module, waiting...")
        time.sleep(1)

    logger.info("Using validation module: %s", vm_url)

    obj = CounterAPIValidation.objects.select_related("core").get(pk=pk)
    obj.core.status = ValidationStatus.RUNNING
    obj.core.save()

    start = time.monotonic()
    req_url = obj.get_url()
    logger.debug("Requesting URL: %s", req_url)
    resp = None
    lock = create_validation_module_lock(vm_url)
    lock.acquire(blocking=True)
    try:
        resp = requests.post(vm_url + "sushi.php", json={"url": req_url})
        resp.raise_for_status()
    except Exception as e:
        obj.core.status = ValidationStatus.FAILURE
        obj.core.error_message = str(e)
        logger.warning("Error while requesting URL: %s", e)
        if resp:
            logger.warning("Response text: %s", resp.text)
    else:
        json = resp.json()
        obj.core.stats = obj.add_result(json.get("result", {}))
        obj.core.used_memory = json.get("memory", 0)
        obj.core.status = ValidationStatus.SUCCESS
        if header := json.get("result", {}).get("header"):
            obj.core.cop_version = header.get("cop_version", "")
            obj.core.report_code = header.get("report_id", "")
        if report := json.get("report"):
            # report is base64 encoded zlib compressed JSON
            content = zlib.decompress(base64.b64decode(report.encode("utf-8")))
            obj.core.file_checksum = checksum_bytes(content)
            obj.core.file_size = len(content)
            obj.file = SimpleUploadedFile(name="foo.json", content=content)
            obj.filename = f'Counter API {obj.core.created.strftime("%Y-%m-%d %H:%M:%S")}'
    finally:
        lock.release()
        end = time.monotonic()
        obj.core.duration = end - start
        obj.core.save()
        obj.save()


@celery.shared_task(base=ValidationTask)
def expired_validations_cleanup():
    logger.info("Removed expired validations: %s", Validation.objects.expired().delete()[1])
