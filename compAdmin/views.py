from rest_framework import generics, views
from rest_framework.permissions import IsAdminUser

from core.permissions import IsCompetitionSuperAdminOrIsAdmin
from .serializers import *


class PointTemplates(generics.ListCreateAPIView):
    permission_classes = [IsCompetitionSuperAdminOrIsAdmin]
    serializer_class = PointTemplateSerializer
    name = 'points-templates-list'

    def get_queryset(self):
        if self.request.user.is_staff:
            return PointTemplate.objects.all()
        else:
            comp__id = self.request.user.competition.id
            return PointTemplate.objects.filter(competition__id=comp__id)


class CompGroupView(generics.ListCreateAPIView):
    serializer_class = CompGroupSerializer
    permission_classes = [IsCompetitionSuperAdminOrIsAdmin]
    name = 'compgroup-list'

    def get_queryset(self):
        if self.request.user.is_staff:
            return CompGroup.objects.all()
        else:
            comp__id = self.request.user.competition.id
            return CompGroup.objects.filter(competition__id=comp__id)


class CompAdminView(generics.ListCreateAPIView):
    serializer_class = CompAdminSerializer
    permission_classes = [IsCompetitionSuperAdminOrIsAdmin]
    name = 'competition-admin-api'

    # permission_classes_by_action = {'create': [IsCompetitionSuperAdminOrIsAdmin],
    #                                 'list': [IsCompetitionSuperAdminOrIsAdmin]}

    def get_queryset(self):
        if self.request.user.is_staff:
            return CompAdmin.objects.all()
        else:
            comp__id = self.request.user.competition.id
            return CompAdmin.objects.filter(competition__id=comp__id)
