from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_condition import Or

from core.permissions import IsCompetitionSuperAdmin, IsCompetitionAdmin
from .serializers import *


class PointTemplates(viewsets.ModelViewSet):
    serializer_class = PointTemplateSerializer
    name = 'points-templates-list'
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_staff:
            return PointTemplate.objects.all()
        else:
            comp = self.request.user.competition
            return PointTemplate.objects.filter(competition=comp)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create']:
            return Or(IsAdminUser(), IsCompetitionSuperAdmin()),
        else:
            return Or(IsAdminUser(), IsCompetitionAdmin()),


class CompGroupView(viewsets.ModelViewSet):
    serializer_class = CompGroupSerializer
    permission_classes = [Or(IsAdminUser, IsCompetitionAdmin)]
    name = 'comp-group-list'
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_staff:
            return CompGroup.objects.all()
        else:
            comp = self.request.user.competition
            return CompGroup.objects.filter(competition=comp)


class CompAdminView(viewsets.ModelViewSet):
    permission_classes = [Or(IsCompetitionSuperAdmin, IsAdminUser)]
    name = 'competition-admin-api'
    lookup_field = 'username'

    def get_queryset(self):
        if self.request.user.is_staff:
            return CompAdmin.objects.all()
        else:
            comp = self.request.user.competition
            return CompAdmin.objects.filter(competition=comp)

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return CompAdminRetrieveUpdateSerializer
        else:
            return CompAdminSerializer
