import os

import celery
import requests
from django.conf import settings
from django.db import transaction

from core.classes.registry import RegistrySync
from core.models import FileValidation


@celery.shared_task
@transaction.atomic
def update_registry_models(cls=None):
	if cls is None:
		cls = RegistrySync()
	cls.sync()


@celery.shared_task
def validate_file(pk):
	obj = FileValidation.objects.get(pk=pk)
	obj.status = FileValidation.StatusEnum.RUNNING
	obj.save()

	with obj.file.open("rb") as fp:
		req = requests.post(
			settings.CTOOLS_URL,
			params={"extension": os.path.splitext(obj.filename)[1].lstrip(".")},
			data=fp,
		)
	req.raise_for_status()

	json = req.json()
	obj.headers = json["headers"]
	obj.messages = json["messages"]
	obj.memory = json["memory"]
	obj.status = FileValidation.StatusEnum.SUCCESS
	obj.save()
