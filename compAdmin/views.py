from django.db.models import QuerySet, Sum
from rest_condition import Or
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.permissions import IsCompetitionSuperAdmin, IsCompetitionAdmin
from core.views import StandardResultsSetPagination, ChangePasswordViewSet, CompetitionView
from student.models import PointRecord
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


# class PointFormatView(viewsets.ModelViewSet):
#     pagination_class = StandardResultsSetPagination
#     queryset = PointFormat.objects.all()
#     serializer_class = PointFormatSerializer
#     permission_classes = [IsAdminUser]
#     name = 'points-templates-list'
#     lookup_field = 'id'


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
        if self.action in ['list', 'update', 'partial_update', 'retrieve']:
            return Or(IsCompetitionAdmin(), IsAdminUser()),
        else:
            return Or(IsCompetitionSuperAdmin(), IsAdminUser()),


class CompAdminView(ChangePasswordViewSet):
    pagination_class = StandardResultsSetPagination
    permission_classes = [Or(IsCompetitionSuperAdmin, IsAdminUser)]
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


class AdminCompetitionView(CompetitionView):
    permission_classes = [IsCompetitionAdmin]

    @action(detail=False, name='General Comp Stats')
    def general_stats(self, request, *args, **kwargs):
        competition = self.request.user.competition
        ramadan_date = 1  # TODO: put ramadan latest date instead of one
        stats = dict()
        top_on_day = StudentUser.objects.filter(competition=competition) \
            .values('username', 'first_name', 'last_name', 'student_points', 'student_points__ramadan_record_date') \
            .filter(student_points__ramadan_record_date=ramadan_date) \
            .annotate(points_per_day=Sum('student_points__point_total')) \
            .order_by('-points_per_day').first()

        stats['top_student_last_day'] = top_on_day
        stats['top_ramadan_day'] = PointRecord.objects.filter(point_template__competition=competition) \
            .values('ramadan_record_date') \
            .annotate(total_day=Sum('point_total')).order_by('-total_day').first()
        stats['students_count'] = StudentUser.objects.count()
        stats['ramadan_date'] = 1  # TODO: put ramadan latest date instead of one
        return Response({**stats})
