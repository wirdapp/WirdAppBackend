from core.my_view import MyModelViewSet
from member_panel.models import PointRecord
from member_panel.serializers import PointRecordSerializer


class PointRecordsView(MyModelViewSet):
    serializer_class = PointRecordSerializer

    def get_queryset(self):
        return PointRecord.objects.all()
