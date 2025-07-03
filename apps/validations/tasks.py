import logging
import os
import time
import uuid

import celery
import requests
from celery.contrib.django.task import DjangoTask

from apps.core.tasks import async_mail_admins
from validations.enums import ValidationStatus
from validations.models import CounterAPIValidation, Validation
from validations.validation_module_api import update_validation_result
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
        obj.core.save(update_fields=["status", "error_message", "duration"])
        async_mail_admins.delay(
            "Validation failed",
            f"Validation {obj.id} failed: {obj.core.error_message}",
        )
        return
    finally:
        lock.release()

    end = time.monotonic()
    try:
        logger.debug("Validation result: %s", req.json())
        update_validation_result(obj, req.json(), end - start)
    except Exception as e:
        obj.core.status = ValidationStatus.FAILURE
        obj.core.error_message = str(e)
        obj.core.save(update_fields=["status", "error_message", "duration"])
        async_mail_admins.delay(
            "Validation update failed",
            f"Validation {obj.id} update failed: {obj.core.error_message}",
        )


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
        end = time.monotonic()
        obj.core.duration = end - start
        obj.core.save()
        obj.save()
        async_mail_admins.delay(
            "Validation failed",
            f"Validation {obj.id} failed: {obj.core.error_message}",
        )
        return
    finally:
        lock.release()

    end = time.monotonic()
    try:
        update_validation_result(obj, resp.json(), end - start)
    except Exception as e:
        obj.core.status = ValidationStatus.FAILURE
        obj.core.error_message = str(e)
        obj.core.save(update_fields=["status", "error_message", "duration"])
        async_mail_admins.delay(
            "Validation update failed",
            f"Validation {obj.id} update failed: {obj.core.error_message}",
        )


@celery.shared_task(base=ValidationTask)
def expired_validations_cleanup():
    logger.info("Removed expired validations: %s", Validation.objects.expired().delete()[1])
