from django.db.models import QuerySet
from rest_condition import Or
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from core.permissions import IsCompetitionSuperAdmin, IsCompetitionAdmin
from core.views import StandardResultsSetPagination, ChangePasswordSerializer
from .serializers import *


class SectionView(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    permission_classes = [Or(IsCompetitionSuperAdmin, IsAdminUser)]
    serializer_class = SectionSerializer
    name = 'section-list'
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Section.objects.all()
        else:
            comp = self.request.user.competition
            return comp.competition_sections.all()


class PointFormatView(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    queryset = PointFormat.objects.all()
    serializer_class = PointFormatSerializer
    permission_classes = [IsAdminUser]
    name = 'points-templates-list'
    lookup_field = 'id'


class PointTemplatesView(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = PointTemplateSerializer
    name = 'points-templates-list'
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_staff:
            return PointTemplate.objects.all()
        else:
            comp = self.request.user.competition
            return comp.competition_point_templates.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return Or(IsAdminUser(), IsCompetitionAdmin()),
        else:
            return Or(IsAdminUser(), IsCompetitionSuperAdmin()),


class CompGroupView(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = CompGroupSerializer
    name = 'comp-group-list'
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_staff:
            return CompGroup.objects.all()
        else:
            user = self.request.user
            if hasattr(user, 'competition_admins'):
                admin = user.competition_admins
                if admin.is_super_admin:
                    return admin.competition.competition_groups.all()
                else:
                    return admin.managed_groups.all()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'retrieve']:
            return Or(IsCompetitionAdmin(), IsAdminUser()),
        else:
            return Or(IsCompetitionSuperAdmin(), IsAdminUser()),


class CompAdminView(ChangePasswordSerializer):
    pagination_class = StandardResultsSetPagination
    name = 'competition-admin-api'
    lookup_field = 'username'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CompAdmin.objects.all()
        else:
            if hasattr(user, 'competition_admins'):
                admin = user.competition_admins
                if admin.is_super_admin:
                    return QuerySet(admin)
                else:
                    return QuerySet(admin).filter(username=admin.username)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', 'retrieve']:
            return CompAdminRetrieveUpdateSerializer
        elif self.action == "change_password":
            return CompAdminChangePasswordSerializer
        else:
            return CompAdminSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'retrieve']:
            return Or(IsCompetitionAdmin(), IsAdminUser()),
        else:
            return Or(IsCompetitionSuperAdmin(), IsAdminUser()),
