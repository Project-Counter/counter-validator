from core.permissions import HasUserAPIKey
from django.db.transaction import atomic
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

import validations.serializers
from validations.filters import (
    MessagesSearchFilter,
    OrderByFilter,
    SeverityFilter,
    ValidationAPIEndpointFilter,
    ValidationCoPVersionFilter,
    ValidationOrderByFilter,
    ValidationReportCodeFilter,
    ValidationSourceFilter,
    ValidationValidationResultFilter,
)
from validations.models import Validation, ValidationCore, ValidationMessage
from validations.serializers import (
    CounterAPIValidationCreateSerializer,
    FileValidationCreateSerializer,
)
from validations.tasks import validate_counter_api, validate_file


class StandardPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 1000


class ValidationViewSet(DestroyModelMixin, ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated | HasUserAPIKey]
    serializer_class = validations.serializers.ValidationSerializer
    pagination_class = StandardPagination
    filter_backends = [
        ValidationOrderByFilter,
        ValidationValidationResultFilter,
        ValidationCoPVersionFilter,
        ValidationReportCodeFilter,
        ValidationAPIEndpointFilter,
        ValidationSourceFilter,
    ]

    def get_serializer_class(self):
        if self.action == "list":
            return validations.serializers.ValidationSerializer
        return validations.serializers.ValidationDetailSerializer

    def get_queryset(self):
        qs = (
            self.request.user.validation_set.current()
            .select_related("core")
            .annotate_source()
            .prefetch_related("counterapivalidation")
            .defer("result_data")
            .order_by("-core__created")
        )
        if self.action not in ("sushi", "file"):
            qs = qs.select_related("core__platform")
        if self.action == "detail":
            qs = qs.defer(None)
        return qs

    @action(detail=False, methods=("POST",), url_path="file")
    @atomic
    def file(self, request):
        serializer = FileValidationCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        validate_file.delay_on_commit(obj.pk)
        out_serializer = self.get_serializer(obj)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=("GET",), url_path="stats")
    def stats(self, request, pk=None):
        validation: Validation = self.get_object()
        stats = {
            "summary": validation.get_summary_stats(),
            "summary_severity": validation.get_summary_severity_stats(),
        }
        return Response(stats)


class CounterAPIValidationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated | HasUserAPIKey]
    serializer_class = validations.serializers.ValidationSerializer

    def create(self, request, *args, **kwargs):
        serializer = CounterAPIValidationCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        validate_counter_api.delay_on_commit(obj.pk)
        out_serializer = self.get_serializer(obj)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class ValidationCoreViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = validations.serializers.ValidationCoreSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return ValidationCore.objects.select_related("platform").order_by("-created")

    @action(detail=False, methods=("GET",))
    def stats(self, request):
        stats = ValidationCore.get_stats()
        return Response(stats)

    @action(detail=False, methods=("GET",), url_path="time-stats")
    def time_stats(self, request):
        stats = ValidationCore.get_time_stats()
        return Response(stats)

    @action(detail=False, methods=("GET",), url_path="split-stats")
    def split_stats(self, request):
        stats = ValidationCore.get_split_stats()
        return Response(stats)


class ValidationMessageViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = validations.serializers.ValidationMessageSerializer
    pagination_class = StandardPagination
    filter_backends = [OrderByFilter, SeverityFilter, MessagesSearchFilter]
    search_fields = ["message", "hint", "summary", "data"]

    def get_queryset(self):
        validation = get_object_or_404(
            Validation.objects.filter(user=self.request.user), pk=self.kwargs["validation_pk"]
        )
        return ValidationMessage.objects.filter(validation=validation)
