import logging
from datetime import timedelta

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from dj_rest_auth.views import PasswordResetConfirmView
from django.db.models import Count, Exists, OuterRef, Subquery, Value
from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from validations.models import ValidationCore

from . import serializers
from .changelog import get_changelog_entries
from .models import User, UserApiKey
from .permissions import IsValidatorAdminUser
from .serializers import UserSerializer
from .signals import password_reset_signal
from .version import get_server_version, get_upstream_version

logger = logging.getLogger(__name__)


class UserApiKeyViewSet(ModelViewSet):
    lookup_field = "prefix"
    serializer_class = serializers.UserApiKeySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.userapikey_set

    def create(self, request, *_, **__):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        _, key = UserApiKey.objects.create_key(**serializer.validated_data, user=self.request.user)
        return Response({"key": key}, status=status.HTTP_201_CREATED)

    def destroy(self, *_, **__):
        obj = self.get_object()
        if obj.revoked:
            raise ValidationError(detail="This API key has already been revoked")
        obj.revoked = True
        obj.save()
        return Response(self.get_serializer(obj).data)


class UserDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    allowed_methods = ("GET", "PUT", "PATCH")

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get(self, request, **kwargs):
        return Response(UserSerializer(request.user).data)

    def put(self, request, **kwargs):
        email_verified_before = request.user.verified_email
        serializer = UserSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # if the email was changed, we need to re-verify it
        if email_verified_before and not request.user.verified_email:
            email, _created = EmailAddress.objects.get_or_create(
                user=request.user, email=request.user.email
            )
            email.send_confirmation(request)
        return Response(serializer.data)

    def patch(self, request, **kwargs):
        return self.put(request, **kwargs)

    def delete(self, request, **kwargs):
        user = request.user
        if user.is_superuser and User.objects.filter(is_superuser=True).count() == 1:
            raise PermissionDenied(
                "You cannot delete your own account - you are the last superuser"
            )
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserManagementViewSet(ModelViewSet):
    serializer_class = serializers.UserSerializer
    permission_classes = (IsValidatorAdminUser,)

    def get_queryset(self):
        """
        Only superusers can see other superusers.
        """
        qs = User.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.exclude(is_superuser=True)
        cutoff_date = now() - timedelta(days=7)
        qs = qs.annotate(
            _verified_email=Exists(
                EmailAddress.objects.filter(
                    user_id=OuterRef("id"), email=OuterRef("email"), verified=True
                )
            ),
            validations_total=Subquery(
                ValidationCore.objects.filter(user_id=OuterRef("id"))
                .order_by()
                .annotate(x=Value(1))
                .values("x")
                .annotate(count=Count("id"))
                .values("count")
            ),
            validations_last_week=Subquery(
                ValidationCore.objects.filter(user_id=OuterRef("id"), created__gte=cutoff_date)
                .order_by()
                .annotate(x=Value(1))
                .values("x")
                .annotate(count=Count("id"))
                .values("count")
            ),
        )
        return qs

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise PermissionDenied("You cannot delete your own account")
        super().perform_destroy(instance)

    @action(detail=True, methods=["post"], url_name="send-invitation", url_path="send-invitation")
    def send_invitation(self, request, pk=None):
        user = self.get_object()
        adapter = get_adapter()
        adapter.send_invitation_email(request, user)
        return Response({"detail": "Invitation sent"}, status=status.HTTP_200_OK)


class UserPasswordResetView(PasswordResetConfirmView):
    """
    We have to extend the rest-auth `PasswordResetConfirmView` in order to emit a signal
    on successful reset
    """

    def post(self, request, *args, **kwargs):
        """
        We extend the parent implementation in order to insert a signal. Unfortunately we have
        to duplicate part of the parent code, but it is probably better than replacing it
        completely
        """
        # serialization is done in parent method as well, but we do it once more to get to the
        # user instance which we need for the signal
        # also, we need to do the serialization before we call super().post, because once
        # it is fully processed, the token will no longer be valid and validation will fail
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()  # populates serializer.user
        response = super().post(request, *args, **kwargs)
        password_reset_signal.send(self.__class__, request=request, user=serializer.user)
        return response


class VersionView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            server_version = get_server_version()
        except Exception as e:
            logger.error("Failed to get server version", exc_info=e)
            server_version = None

        try:
            upstream_version = get_upstream_version()
        except Exception as e:
            logger.error("Failed to get upstream version", exc_info=e)
            upstream_version = None
        return Response({"server": server_version, "upstream": upstream_version})


class ChangelogView(APIView):
    permission_classes = []

    def get(self, request):
        return Response(get_changelog_entries())
