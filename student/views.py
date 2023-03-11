import itertools

from django.db.models import Q
from rest_framework import permissions, viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from compAdmin.serializers import PointTemplateSerializer
from core import util
from core.permissions import NoPermission
from core.util import current_hijri_date
from core.views import user_points_stats
from .serializers import *


class PointRecordsView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointRecordSerializer
    name = 'points-record-list'
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        date = self.request.query_params['date'] if 'date' in self.request.query_params else util.current_hijri_date
        if hasattr(user, 'competition_students'):
            student = user.competition_students
            points = student.student_points.filter(point_scored_units__gte=0)
            if self.action == 'list':
                return points.filter(ramadan_record_date=date)
            else:
                return points
        else:
            return PointRecord.objects.none()

    @action(detail=False, name='Point Scores Stats')
    def points_stats(self, request, *args, **kwargs):
        user = self.request.user
        stats_type = self.request.query_params['type'] if 'type' in self.request.query_params else ''
        date = self.request.query_params['date'] if 'date' in self.request.query_params else None
        return user_points_stats(user, stats_type, date)


class StudentUserView(viewsets.ModelViewSet):
    name = 'student-user-list'
    lookup_field = 'username'
    http_method_names = ['get', 'put', 'post', 'options']

    def destroy(self, request, *args, **kwargs):
        util.destroy(self.get_object())

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'competition_students'):
            return StudentUser.objects.filter(username=user.username, is_active=True)
        else:
            return StudentUser.objects.none()

    def get_serializer_class(self):
        if self.action in ['create']:
            return StudentUserSerializer
        elif self.action in ['update', 'partial_update', 'retrieve']:
            return StudentUpdateSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return AllowAny(),
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return IsAuthenticated(),
        else:
            return NoPermission(),


class PointTemplatesView(viewsets.ReadOnlyModelViewSet):
    serializer_class = PointTemplateSerializer
    name = 'points-templates-list'
    lookup_field = 'id'

    def get_queryset(self):
        comp = self.request.user.competition
        return comp.competition_point_templates\
            .filter(is_active=True) \
            .filter(is_shown=True) \
            .filter(Q(custom_days__contains=current_hijri_date) or Q(custom_days=''))

    def get_permissions(self):
        return IsAuthenticated(),

    def list(self, request, *args, **kwargs):
        query = self.get_queryset().all().select_related('section')
        grouping_func = lambda pt: pt.section_id
        sections = self.request.user.competition.competition_sections.values('id', 'label')
        res = dict()
        for section_id, point_templates in itertools.groupby(query, grouping_func):
            res[sections.get(id=section_id)['label']] = [PointTemplateSerializer(pt).data for pt in point_templates]
        return Response({**res})


class AnnouncementsView(viewsets.ReadOnlyModelViewSet):
    name = 'announcements-list'

    def list(self, request, *args, **kwargs):
        user = self.request.user
        competition = user.competition
        comp_group = user.competition_students.group

        announcements = comp_group.announcements.split(';') if comp_group else []
        announcements = announcements + competition.announcements.split(';')
        return Response({'announcements': announcements})

    def get_permissions(self):
        return IsAuthenticated(),


class GroupAdminInformationView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        result = dict()
        user = self.request.user.competition_students
        admin = user.group.admin
        result['username'] = admin.username
        result['first_name'] = admin.first_name
        result['last_name'] = admin.last_name
        result['email'] = admin.email
        result['phone_number'] = admin.phone_number
        return Response({**result})
