from core.permissions import HasUserAPIKey, IsValidatorAdminUser
from django.db.transaction import atomic
from django.http import HttpResponseForbidden
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from validations.filters import (
    OrderByFilter,
    SeverityFilter,
    ValidationAPIEndpointFilter,
    ValidationCoPVersionFilter,
    ValidationCoreAPIEndpointFilter,
    ValidationCoreCoPVersionFilter,
    ValidationCoreReportCodeFilter,
    ValidationCoreSourceFilter,
    ValidationCoreValidationResultFilter,
    ValidationOrderByFilter,
    ValidationPublishedFilter,
    ValidationReportCodeFilter,
    ValidationSourceFilter,
    ValidationValidationResultFilter,
)
from validations.models import Validation, ValidationCore, ValidationMessage
from validations.serializers import (
    CounterAPIValidationCreateSerializer,
    FileValidationCreateSerializer,
    PublicValidationDetailSerializer,
    ValidationCoreSerializer,
    ValidationDetailSerializer,
    ValidationMessageSerializer,
    ValidationSerializer,
    ValidationWithUserSerializer,
)
from validations.tasks import validate_counter_api, validate_file


class StandardPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 1000


class ValidationViewSet(DestroyModelMixin, ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated | HasUserAPIKey]
    serializer_class = ValidationSerializer
    pagination_class = StandardPagination
    filter_backends = [
        ValidationOrderByFilter,
        ValidationValidationResultFilter,
        ValidationCoPVersionFilter,
        ValidationReportCodeFilter,
        ValidationAPIEndpointFilter,
        ValidationSourceFilter,
        ValidationPublishedFilter,
        SearchFilter,
    ]
    search_fields = ["user_note", "user__first_name", "user__last_name", "user__email"]

    def get_serializer_class(self):
        if self.action == "list":
            return ValidationSerializer
        return ValidationDetailSerializer

    def get_queryset(self, list_all=False):
        base = self.request.user.validation_set
        if (self.detail or list_all) and (
            self.request.user.is_superuser or self.request.user.is_validator_admin
        ):
            # admins can see details of all validations, and can also list them all
            # via a dedicated endpoint (which uses the `list_all` attr)
            #
            # but using the normal api, they get list of their own like everybody else
            base = Validation.objects.all()
        qs = (
            base.current()
            .select_related("core")
            .annotate_source()
            .prefetch_related("counterapivalidation")
            .defer("result_data")
            .order_by("-core__created")
        )
        if self.detail:
            qs = qs.defer(None)
        return qs

    @action(
        detail=False,
        methods=["get"],
        url_path="all",
        permission_classes=[IsValidatorAdminUser],
    )
    def list_all(self, request):
        """
        This is an almost one-to-one copy of the list method from `ListModelMixin`, but it passes
        the `list_all` attribute to `get_queryset`.
        """
        queryset = self.filter_queryset(self.get_queryset(list_all=True).select_related("user"))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ValidationWithUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

    @action(detail=True, methods=("POST",), url_path="publish")
    def publish(self, request, pk=None):
        validation: Validation = self.get_object()
        validation.publish()
        return Response(self.get_serializer(validation).data)

    @action(detail=True, methods=("POST",), url_path="unpublish")
    def unpublish(self, request, pk=None):
        validation: Validation = self.get_object()
        validation.unpublish()
        return Response(self.get_serializer(validation).data)


class PublicValidationViewSet(ReadOnlyModelViewSet):
    permission_classes = []
    serializer_class = PublicValidationDetailSerializer
    lookup_field = "public_id"

    def get_queryset(self):
        return (
            Validation.objects.current()
            .public()
            .select_related("core")
            .annotate_source()
            .prefetch_related("counterapivalidation")
            .defer("result_data")
            .order_by("-core__created")
        )

    def list(self, request, *args, **kwargs):
        return HttpResponseForbidden({"detail": "Listing public validations is not allowed."})


class CounterAPIValidationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated | HasUserAPIKey]
    serializer_class = ValidationSerializer

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
    permission_classes = [IsValidatorAdminUser]
    serializer_class = ValidationCoreSerializer
    pagination_class = StandardPagination
    filter_backends = [
        OrderByFilter,
        ValidationCoreSourceFilter,
        ValidationCoreCoPVersionFilter,
        ValidationCoreValidationResultFilter,
        ValidationCoreReportCodeFilter,
        ValidationCoreAPIEndpointFilter,
    ]

    def get_queryset(self):
        return ValidationCore.objects.order_by("-created")

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
    serializer_class = ValidationMessageSerializer
    pagination_class = StandardPagination
    filter_backends = [OrderByFilter, SeverityFilter, SearchFilter]
    search_fields = ["message", "hint", "summary", "data"]

    def get_queryset(self):
        validation = get_object_or_404(
            Validation.objects.filter(user=self.request.user), pk=self.kwargs["validation_pk"]
        )
        return ValidationMessage.objects.filter(validation=validation)
