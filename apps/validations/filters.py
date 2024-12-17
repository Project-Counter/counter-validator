"""
Basic filters for the REST API.
"""

import logging
import operator
from functools import reduce

from django.db.models import Q
from rest_framework import filters

from validations.enums import SeverityLevel

logger = logging.getLogger(__name__)


# base filter classes


def is_truthy(value: str | None, extra_values=None):
    return value in ("true", "1", "True") + (extra_values or ())


class OrderByFilter(filters.BaseFilterBackend):
    """
    A filter backend that allows ordering by fields.
    """

    attr_to_prefix = {}

    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get("order_by", None)
        if ordering:
            ordering = self.attr_to_prefix.get(ordering, "") + ordering
            if is_truthy(request.query_params.get("order_desc", None), extra_values=("desc",)):
                ordering = f"-{ordering}"
            return queryset.order_by(ordering)
        return queryset


class BaseMultiValueFilter(filters.BaseFilterBackend):
    query_param = ""
    attr_name = ""

    def filter_queryset(self, request, queryset, view):
        if not self.query_param:
            raise NotImplementedError("query_param must be set in a subclass")
        attr_name = self.attr_name or self.query_param
        if param := request.query_params.get(self.query_param, "").strip():
            return queryset.filter(**{f"{attr_name}__in": param.split(",")})
        return queryset


class SeverityFilter(filters.BaseFilterBackend):
    """
    A filter backend that allows filtering by severity.
    """

    query_param = "severity"
    attr_name = "severity"

    def filter_queryset(self, request, queryset, view):
        if severities := request.query_params.get(self.query_param, "").split(","):
            values = []
            for severity in severities:
                if severity.isdigit():
                    severity = int(severity)
                if (severity := SeverityLevel.by_any_value(severity)) is not None:
                    values.append(severity)
            if values:
                logger.info(values)
                return queryset.filter(**{f"{self.attr_name}__in": values})
        return queryset


class ValidationCoPVersionFilter(BaseMultiValueFilter):
    """
    A filter that allows filtering Validations by CoP version.
    """

    query_param = "cop_version"
    attr_name = "core__cop_version"


class ValidationCoreCoPVersionFilter(BaseMultiValueFilter):
    """
    A filter that allows filtering Validation Cores by CoP version.
    """

    query_param = "cop_version"


class ValidationReportCodeFilter(BaseMultiValueFilter):
    """
    A filter that allows filtering Validations by report code.
    """

    query_param = "report_code"
    attr_name = "core__report_code"


class ValidationCoreReportCodeFilter(BaseMultiValueFilter):
    """
    A filter that allows filtering Validation Cores by report code.
    """

    query_param = "report_code"


class ValidationAPIEndpointFilter(BaseMultiValueFilter):
    """
    A filter that allows filtering Validations by API endpoint.
    """

    query_param = "api_endpoint"
    attr_name = "core__api_endpoint"


class ValidationCoreAPIEndpointFilter(BaseMultiValueFilter):
    """
    A filter that allows filtering Validation Cores by API endpoint.
    """

    query_param = "api_endpoint"


class ValidationSourceFilter(filters.BaseFilterBackend):
    """
    A filter that allows filtering Validations by source.
    """

    attr_prefix = "core__"

    def filter_queryset(self, request, queryset, view):
        qs = []
        # source is computed on the fly from the presence of sushi_credentials_checksum
        # so we need some extra code for that
        if param := request.query_params.get("data_source", "").strip():
            params = param.split(",")
            for param in params:
                if param == "file":
                    qs.append(Q(**{f"{self.attr_prefix}sushi_credentials_checksum": ""}))
                elif param == "counter_api":
                    qs.append(~Q(**{f"{self.attr_prefix}sushi_credentials_checksum": ""}))
                else:
                    # silently ignore unknown sources
                    logger.warning(f"Unknown source: {param}")
            return queryset.filter(reduce(operator.or_, qs))
        return queryset


class ValidationCoreSourceFilter(ValidationSourceFilter):
    attr_prefix = ""


class ValidationValidationResultFilter(SeverityFilter):
    query_param = "validation_result"
    attr_name = "core__validation_result"


class ValidationCoreValidationResultFilter(SeverityFilter):
    query_param = "validation_result"
    attr_name = "validation_result"


class ValidationOrderByFilter(OrderByFilter):
    attr_to_prefix = {
        "file_size": "core__",
        "created": "core__",
        "validation_result": "core__",
        "expiration_date": "core__",
        "report_code": "core__",
        "cop_version": "core__",
        "status": "core__",
    }


class ValidationPublishedFilter(filters.BaseFilterBackend):
    """
    A filter backend that allows filtering by published status.
    """

    def filter_queryset(self, request, queryset, view):
        if published := request.query_params.get("published"):
            published = is_truthy(published)
        if published:
            return queryset.filter(public_id__isnull=False)
        elif published is False:
            return queryset.filter(public_id__isnull=True)
        return queryset
