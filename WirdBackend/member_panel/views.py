from django.db.models import Q
from rest_condition import And
from rest_framework import mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from admin_panel.serializers import PointTemplateSerializer
from core import util_methods, models_helper
from core.permissions import IsContestMember
from member_panel.models import PointRecord
from member_panel.serializers import PointRecordSerializer


class ResultsByDateView(generics.ListCreateAPIView):
    permission_classes = [And(IsAuthenticated(), IsContestMember())]
    serializer_class = PointRecordSerializer

    def get_queryset(self):
        date = self.kwargs["date"]
        username = util_methods.get_username_from_session(self.request)
        return PointRecord.objects.filter(person__person__username=username, record_date=date) \
            .order_by('point_template__section__position', 'point_template__order_in_section')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["record_date"] = self.kwargs["date"]
        return context


class ReadOnlyPointTemplateView(mixins.ListModelMixin, GenericViewSet):
    name = 'points-templates-list'
    permission_classes = [And(IsAuthenticated(), IsContestMember())]
    serializer_class = PointTemplateSerializer

    def get_queryset(self):
        contest_id = util_methods.get_current_contest_dict(self.request)["id"]
        date = self.kwargs["date"]
        return models_helper.get_contest_point_templates(contest_id) \
            .filter(Q(custom_days__contains=[date]) | Q(custom_days__len=0))
