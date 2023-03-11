from rest_framework.permissions import AllowAny

from core.util_classes import MyModelViewSet
from member_panel.models import PointRecord
from member_panel.serializers import PointRecordSerializer


class PointRecordsView(MyModelViewSet):
    permission_classes = [AllowAny(), ]
    serializer_class = PointRecordSerializer

    def get_queryset(self):
        return PointRecord.objects.all()

    def get_permissions(self):
        return AllowAny(),
