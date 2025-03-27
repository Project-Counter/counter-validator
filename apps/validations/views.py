from core.models import User
from core.permissions import HasUserAPIKey, HasVerifiedEmail, IsValidatorAdminUser
from django.conf import settings
from django.db.models import Q
from django.db.transaction import atomic
from django.http import Http404, HttpResponse, HttpResponseForbidden
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from validations.celery_queue import get_number_of_running_validations, get_validation_queue_length
from validations.export import ValidationXlsxExporter
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
    ValidationSearchFilter,
    ValidationSourceFilter,
    ValidationValidationResultFilter,
)
from validations.models import Validation, ValidationCore, ValidationMessage
from validations.permissions import (
    IsAuthenticatedForListOrCreateAnyForDetail,
    IsValidationOwnerOrIsPublic,
)
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
    permission_classes = [
        HasUserAPIKey | IsAuthenticatedForListOrCreateAnyForDetail,
        IsValidationOwnerOrIsPublic | IsValidatorAdminUser,  # this is per-object permission
    ]
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
        ValidationSearchFilter,
    ]

    def get_serializer_class(self):
        if self.detail:
            return ValidationDetailSerializer
        return ValidationSerializer

    def get_queryset(self, list_all=False):
        # Here are the conditions for visibility of validations:
        # - public validations are visible to everyone with the public_id, but only when self.detail
        # - logged-in users can see their own validations - both list and detail
        # - admins can see all validations - both list and detail

        # permissions should ensure list is not possible for unauthenticated users
        if (
            (self.detail or list_all)
            and self.request.user.is_authenticated
            and self.request.user.has_admin_role
        ):
            # admins can see details of all validations, and can also list them all
            # via a dedicated endpoint (which uses the `list_all` attr)
            #
            # but using the normal api, they get list of their own like everybody else
            base = Validation.objects.all()
        elif not self.detail:
            # list only possible for authenticated users - users can see their own validations
            base = Validation.objects.filter(core__user=self.request.user)
        elif self.request.user.is_authenticated:
            base = Validation.objects.filter(
                Q(core__user=self.request.user) | Q(public_id=self.kwargs["pk"])
            )
        else:
            # only public validations are visible to unauthenticated users in detail
            base = Validation.objects.public().filter(public_id=self.kwargs["pk"])

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

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        except Http404:
            obj = get_object_or_404(Validation, public_id=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

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
        queryset = self.filter_queryset(
            self.get_queryset(list_all=True).select_related("core__user")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ValidationWithUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=("POST",),
        url_path="file",
        permission_classes=[IsAuthenticated | HasUserAPIKey, HasVerifiedEmail],
    )
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

    @action(detail=True, methods=("GET",), url_path="export")
    def export(self, request, pk=None):
        validation: Validation = self.get_object()
        exporter = ValidationXlsxExporter(validation)
        return HttpResponse(
            exporter.export(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=validation-{validation.id}.xlsx"
            },
        )


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


class CounterAPIValidationViewSet(CreateModelMixin, GenericViewSet):
    """
    This viewset is used to create a new validation from a COUNTER API request.
    It is create-only - reading should be done using the ValidationViewSet.
    """

    permission_classes = [IsAuthenticated | HasUserAPIKey, HasVerifiedEmail]
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
        SearchFilter,
    ]
    # which fields to search using the SearchFilter
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    def get_queryset(self):
        return ValidationCore.objects.select_related("user").order_by("-created")

    def _get_stats_kwargs(self, request):
        kwargs = {}
        if user_id := request.query_params.get("user"):
            user = get_object_or_404(User, pk=user_id)
            kwargs["user"] = user
        return kwargs

    @action(detail=False, methods=("GET",))
    def stats(self, request):
        kwargs = self._get_stats_kwargs(request)
        stats = ValidationCore.get_stats(**kwargs)
        return Response(stats)

    @action(detail=False, methods=("GET",), url_path="time-stats")
    def time_stats(self, request):
        kwargs = self._get_stats_kwargs(request)
        stats = ValidationCore.get_time_stats(**kwargs)
        return Response(stats)

    @action(detail=False, methods=("GET",), url_path="split-stats")
    def split_stats(self, request):
        kwargs = self._get_stats_kwargs(request)
        stats = ValidationCore.get_split_stats(**kwargs)
        return Response(stats)


class ValidationMessageViewSet(ReadOnlyModelViewSet):
    # default permission is IsAdminUser, so [] is needed to open it up
    # this is because validations may be public and for those we do not require authentication
    permission_classes = []
    serializer_class = ValidationMessageSerializer
    pagination_class = StandardPagination
    filter_backends = [OrderByFilter, SeverityFilter, SearchFilter]
    search_fields = ["message", "hint", "summary", "data"]

    def get_queryset(self):
        validation = None
        if self.request.user.is_authenticated:
            # for logged-in users, consider the validation id could be their own validation
            validation = Validation.objects.filter(
                core__user=self.request.user, pk=self.kwargs["validation_pk"]
            ).first()
        if not validation:
            # if the validation is not found, or the user is not authenticated,
            # either this is a public validation, or it does not exist for the user
            validation = get_object_or_404(Validation, public_id=self.kwargs["validation_pk"])
        return ValidationMessage.objects.filter(validation=validation)


class ValidationQueueInfo(APIView):
    permission_classes = [IsValidatorAdminUser]

    def get(self, request):
        queue_length = get_validation_queue_length()
        running = get_number_of_running_validations()
        worker_num = len(settings.VALIDATION_MODULES_URLS)
        return Response({"queued": queue_length, "running": running, "workers": worker_num})
