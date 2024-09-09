from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DrfValidationError
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
	if isinstance(exc, DjangoValidationError):
		exc = DrfValidationError(as_serializer_error(exc))
	return drf_exception_handler(exc, context)
