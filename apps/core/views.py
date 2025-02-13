import logging

from allauth.account.models import EmailAddress
from django.db.models import Exists, OuterRef
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from . import serializers
from .models import User, UserApiKey
from .permissions import IsValidatorAdminUser
from .serializers import UserSerializer

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
        qs = qs.annotate(
            _verified_email=Exists(
                EmailAddress.objects.filter(
                    user_id=OuterRef("id"), email=OuterRef("email"), verified=True
                )
            )
        )
        return qs

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise PermissionDenied("You cannot delete your own account")
        super().perform_destroy(instance)
