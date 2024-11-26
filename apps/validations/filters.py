"""
Basic filters for the REST API.
"""

from rest_framework import filters

from validations.enums import SeverityLevel


class OrderByFilter(filters.BaseFilterBackend):
    """
    A filter backend that allows ordering by fields.
    """

    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get("order_by", None)
        if request.query_params.get("order_desc", None) in ("true", "1", "desc", "True"):
            ordering = f"-{ordering}"
        if ordering:
            return queryset.order_by(ordering)
        return queryset


class SeverityFilter(filters.BaseFilterBackend):
    """
    A filter backend that allows filtering by severity.
    """

    def filter_queryset(self, request, queryset, view):
        if severities := request.query_params.get("severity", "").split(","):
            values = []
            for severity in severities:
                if severity.isdigit():
                    severity = int(severity)
                if severity := SeverityLevel.by_any_value(severity):
                    values.append(severity)
            if values:
                return queryset.filter(severity__in=values)
        return queryset


class MessagesSearchFilter(filters.SearchFilter):
    """
    A filter backend that allows filtering by text.
    """

    search_param = "search"
