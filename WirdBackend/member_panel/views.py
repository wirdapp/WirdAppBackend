from member_panel.serializers import PolymorphicPointRecordSerializer
from member_panel.model_util import get_member_point_records
from core.util_classes import CustomPermissionsMixin
from rest_framework import viewsets


class MemberPointRecordViewSet(CustomPermissionsMixin, viewsets.ModelViewSet):
    verified_members_allowed_methods = ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
    serializer_class = PolymorphicPointRecordSerializer

    def get_queryset(self):
        return get_member_point_records(self.request)
