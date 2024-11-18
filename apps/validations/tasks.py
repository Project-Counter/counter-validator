import base64
import logging
import os
import time
import uuid
import zlib

import celery
import requests
from celery.contrib.django.task import DjangoTask
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from validations.enums import ValidationStatus
from validations.hashing import checksum_bytes
from validations.models import CounterAPIValidation, Validation, ValidationCore

logger = logging.getLogger(__name__)


class ValidationTask(DjangoTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        obj = Validation.objects.get(pk=args[0])
        obj.status = ValidationStatus.FAILURE
        obj.save()


@celery.shared_task(base=ValidationTask)
def validate_file(pk: uuid.UUID):
    start = time.monotonic()
    obj = Validation.objects.select_related("core").get(pk=pk)
    obj.core.status = ValidationStatus.RUNNING
    obj.core.save()
    # time.sleep(5)

    try:
        with obj.file.open("rb") as fp:
            req = requests.post(
                settings.CTOOLS_URL + "file.php",
                params={"extension": os.path.splitext(obj.filename)[1].lstrip(".")},
                data=fp,
            )
        req.raise_for_status()
    except Exception as e:
        obj.core.status = ValidationStatus.FAILURE
        obj.core.error_message = str(e)
    else:
        json = req.json()
        obj.result_data = json["result"]
        obj.core.used_memory = json["memory"]
        obj.core.status = ValidationStatus.SUCCESS
        obj.core.stats = ValidationCore.extract_stats(json["result"]["messages"])
        if header := json["result"].get("header"):
            obj.core.cop_version = header.get("cop_version", "")
            obj.core.report_code = header.get("report_id", "")
    finally:
        end = time.monotonic()
        obj.core.duration = end - start
        obj.core.save()
        obj.save()


@celery.shared_task(base=ValidationTask)
def validate_counter_api(pk):
    start = time.monotonic()
    obj = CounterAPIValidation.objects.select_related("core").get(pk=pk)
    obj.status = ValidationStatus.RUNNING
    obj.save()

    req_url = obj.get_url()
    logger.debug("Requesting URL: %s", req_url)
    try:
        resp = requests.post(
            settings.CTOOLS_URL + "sushi.php",
            json={"url": req_url},
        )
        resp.raise_for_status()
    except Exception as e:
        obj.core.status = ValidationStatus.FAILURE
        obj.core.error_message = str(e)
        logger.warning("Error while requesting URL: %s", e)
        logger.warning("Response text: %s", resp.text)
    else:
        json = resp.json()
        obj.result_data = json["result"]
        obj.core.used_memory = json["memory"]
        obj.core.status = ValidationStatus.SUCCESS
        obj.core.stats = ValidationCore.extract_stats(json["result"]["messages"])
        if header := json["result"].get("header"):
            obj.core.cop_version = header.get("cop_version", "")
            obj.core.report_code = header.get("report_id", "")
        if report := json.get("report"):
            # report is base64 encoded gzipped JSON
            logger.info("Decoding report: %s", report)
            content = zlib.decompress(base64.b64decode(report.encode("utf-8")))
            obj.core.file_checksum = checksum_bytes(content)
            obj.core.file_size = len(content)
            obj.file = SimpleUploadedFile(name="foo.json", content=content)
            obj.filename = f'Counter API Report {obj.core.created.strftime("%Y-%m-%d %H:%M:%S")}'
    finally:
        end = time.monotonic()
        obj.core.duration = end - start
        obj.core.save()
        obj.save()
