# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

import counter.serializers
from counter.models import Platform, SushiService


class PlatformViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return counter.serializers.PlatformSimpleSerializer
        return counter.serializers.PlatformSerializer

    def get_queryset(self):
        qs = Platform.objects.all()
        if self.action == "detail":
            qs = qs.prefetch_related("reports", "sushi_services")
        return qs


class SushiServiceViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return counter.serializers.SushiServiceSerializer
        return counter.serializers.SushiServiceSerializer

    def get_queryset(self):
        qs = SushiService.objects.all()
        # if self.action == "detail":
        # 	qs = qs.prefetch_related("reports", "sushi_services")
        return qs
