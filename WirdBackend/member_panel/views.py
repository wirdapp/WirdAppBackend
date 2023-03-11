from rest_condition import And
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from admin_panel.serializers import PointTemplateSerializer
from core import util_methods, models_helper
from core.permissions import IsContestMember
from core.util_classes import MyModelViewSet
from member_panel.models import PointRecord
from member_panel.serializers import PointRecordSerializer


class PointRecordsView(MyModelViewSet):
    super_admin_allowed_methods = []
    admin_allowed_methods = []
    member_allowed_methods = ['retrieve', 'list', 'create', 'update', 'partial_update']
    serializer_class = PointRecordSerializer

    def get_queryset(self):
        username = util_methods.get_username_from_session(self.request)
        return PointRecord.objects.filter(person__person__username=username)


class ReadOnlyPointTemplateView(mixins.ListModelMixin, GenericViewSet):
    name = 'points-templates-list'
    permission_classes = [And(IsAuthenticated(), IsContestMember())]
    serializer_class = PointTemplateSerializer

    def get_queryset(self):
        contest_id = util_methods.get_current_contest_dict(self.request)["id"]
        # TODO: Filter by custom_days
        return models_helper.get_contest_point_templates(contest_id)
