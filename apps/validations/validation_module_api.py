import base64
import logging
import zlib

from core.tasks import async_mail_admins
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

from validations.enums import SeverityLevel, ValidationStatus
from validations.hashing import checksum_bytes
from validations.models import Validation

logger = logging.getLogger(__name__)

#
# Dates are simply parsed as strings - we do not need to parse them
#
# In messages, we are very relaxed about missing values - we do not
# need to enforce them to be present
#
# The header may be empty in case of a really broken file
# so we make all the fields optional
#


class HeaderSerializer(serializers.Serializer):
    cop_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    report_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    institution_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    created = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    created_by = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    begin_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    end_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    format = serializers.ChoiceField(choices=["tabular", "json"], required=False, allow_blank=True)
    result = serializers.ListField(
        child=serializers.CharField(allow_blank=True), required=False, allow_empty=True
    )  # list of strings
    report = serializers.DictField(required=False, allow_null=True, allow_empty=True)


class MessageSerializer(serializers.Serializer):
    l = serializers.ChoiceField(choices=SeverityLevel.labels)  # noqa E741, severity
    m = serializers.CharField(allow_blank=True)  # message
    s = serializers.CharField(allow_blank=True)  # summary
    p = serializers.CharField(allow_blank=True, allow_null=True)  # location
    h = serializers.CharField(allow_blank=True, allow_null=True)  # hint
    d = serializers.CharField(allow_blank=True, allow_null=True)  # data


class ResultSerializer(serializers.Serializer):
    header = HeaderSerializer()
    messages = MessageSerializer(many=True)
    result = serializers.ChoiceField(choices=SeverityLevel.labels)
    datetime = serializers.CharField()


class ValidationResultSerializer(serializers.Serializer):
    result = ResultSerializer()
    memory = serializers.IntegerField(default=0)
    report = serializers.CharField(required=False, allow_null=True)


def decode_report_file(report: str) -> bytes:
    return zlib.decompress(base64.b64decode(report.encode("utf-8")))


def update_validation_result(validation: Validation, result: dict, duration: float):
    serializer = ValidationResultSerializer(data=result)
    validation.core.duration = duration
    if not serializer.is_valid():
        # send email to admins - this may be a bug in the validation module
        # or in the API
        logger.warning("Validation module returned invalid result: %s", serializer.errors)
        async_mail_admins(
            "Validation module returned invalid result",
            f"Validation {validation.id} returned invalid result: {serializer.errors}",
        )
        validation.core.status = ValidationStatus.FAILURE
        validation.core.error_message = str(serializer.errors)
        validation.core.save(update_fields=["status", "error_message", "duration"])
        return
    data = serializer.validated_data
    validation.core.stats = validation.add_result(data["result"])
    validation.core.used_memory = data["memory"]
    validation.core.status = ValidationStatus.SUCCESS
    if header := data["result"].get("header", {}):
        # replace potentially null values with ""
        validation.core.cop_version = header.get("cop_version", "") or ""
        validation.core.report_code = header.get("report_id", "") or ""
    if (report := data.get("report")) and hasattr(validation, "file"):
        # only set the file if the Validation object has a file field
        # this should be always true when the `report` is present
        # but we want to make 100% sure
        #
        # report is base64 encoded zlib compressed JSON
        content = decode_report_file(report)
        validation.core.file_checksum = checksum_bytes(content)
        validation.core.file_size = len(content)
        validation.file = SimpleUploadedFile(name="foo.json", content=content)
        validation.filename = f"Counter API {validation.core.created.strftime('%Y-%m-%d %H:%M:%S')}"
    validation.core.save()
    validation.save()
