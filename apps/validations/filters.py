"""
Basic filters for the REST API.
"""

import logging

from rest_framework import filters

from validations.enums import SeverityLevel

logger = logging.getLogger(__name__)


# base filter classes


class OrderByFilter(filters.BaseFilterBackend):
    """
    A filter backend that allows ordering by fields.
    """

    attr_to_prefix = {}

    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get("order_by", None)
        if ordering:
            ordering = self.attr_to_prefix.get(ordering, "") + ordering
            if request.query_params.get("order_desc", None) in ("true", "1", "desc", "True"):
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
                if severity := SeverityLevel.by_any_value(severity):
                    values.append(severity)
            if values:
                logger.info(values)
                return queryset.filter(**{f"{self.attr_name}__in": values})
        return queryset


class MessagesSearchFilter(filters.SearchFilter):
    """
    A filter backend that allows filtering by text.
    """

    search_param = "search"


class ValidationCoPVersionFilter(BaseMultiValueFilter):
    """
    A filter that allows filtering Validations by CoP version.
    """

    query_param = "cop_version"
    attr_name = "core__cop_version"


class ValidationReportCodeFilter(BaseMultiValueFilter):
    """
    A filter that allows filtering Validations by report code.
    """

    query_param = "report_code"
    attr_name = "core__report_code"


class ValidationValidationResultFilter(SeverityFilter):
    query_param = "validation_result"
    attr_name = "core__validation_result"


class ValidationOrderByFilter(OrderByFilter):
    attr_to_prefix = {
        "file_size": "core__",
        "created": "core__",
        "platform_name": "core__",
        "validation_result": "core__",
        "expiration_date": "core__",
        "report_code": "core__",
        "cop_version": "core__",
        "status": "core__",
    }
