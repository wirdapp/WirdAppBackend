from core.my_view import MyModelViewSet
from member_panel.models import PointRecord
from member_panel.serializers import PointTemplatePolymorphicSerializer


class PointRecordsView(MyModelViewSet):
    serializer_class = PointTemplatePolymorphicSerializer

    def get_queryset(self):
        return PointRecord.objects.all()
