from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from compAdmin.serializers import PointTemplateSerializer
from core.permissions import NoPermission
from core.views import StandardResultsSetPagination, user_points_stats
from .serializers import *


class PointRecordsView(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointRecordSerializer
    name = 'points-record-list'
    lookup_field = 'id'
    filterset_fields = ['ramadan_record_date']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'competition_students'):
            return PointRecord.objects.filter(student__username=user.username)
        else:
            return PointRecord.objects.none()

    @action(detail=False, name='Point Scores Stats')
    def points_stats(self, request, *args, **kwargs):
        user = self.request.user
        stats_type = self.request.query_params['type'] if 'type' in self.request.query_params else ''
        return user_points_stats(user, stats_type)


class StudentUserView(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    name = 'student-user-list'
    lookup_field = 'username'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'competition_students'):
            return StudentUser.objects.filter(username=user.username)
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
    pagination_class = StandardResultsSetPagination
    serializer_class = PointTemplateSerializer
    name = 'points-templates-list'
    lookup_field = 'id'

    def get_queryset(self):
        comp = self.request.user.competition
        return comp.competition_point_templates.all()

    def get_permissions(self):
        return IsAuthenticated(),


class AnnouncementsView(viewsets.ReadOnlyModelViewSet):
    name = 'announcements-list'

    def list(self, request, *args, **kwargs):
        anounc = dict()
        user = self.request.user
        competition = user.competition
        comp_groups = CompGroup.objects.filter(competition=competition)

        for cg in comp_groups:
            anounc[cg.name] = cg.announcements.split(';')

        anounc['comp'] = competition.announcements.split(';')
        return Response({'announcements': anounc})

    def get_permissions(self):
        return IsAuthenticated(),
