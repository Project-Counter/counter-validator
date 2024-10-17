import uuid6
from django.db import models


class CreatedUpdatedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDPkMixin(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid6.uuid7)

    class Meta:
        abstract = True
