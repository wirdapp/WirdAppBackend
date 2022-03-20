from django.db.models import Sum
from rest_condition import Or
from rest_framework import viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.permissions import IsCompetitionSuperAdmin, IsCompetitionAdmin
from core.util import current_hijri_date
from core.views import ChangePasswordViewSet
from student.models import PointRecord
from .serializers import *


class SectionView(viewsets.ModelViewSet):
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


class PointTemplatesView(viewsets.ModelViewSet):
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
    permission_classes = [Or(IsCompetitionAdmin, IsAdminUser)]
    name = 'competition-admin-api'
    lookup_field = 'username'
    http_method_names = ['get', 'put', 'post']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CompAdmin.objects.all()
        else:
            if hasattr(user, 'competition_admins'):
                admin = user.competition_admins
                if admin.is_super_admin:
                    return CompAdmin.objects.filter(competition=admin.competition)
                else:
                    return CompAdmin.objects.filter(username=admin.username)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', 'retrieve']:
            return CompAdminRetrieveUpdateSerializer
        elif self.action == "change_password":
            return CompAdminChangePasswordSerializer
        else:
            return CompAdminSerializer


class AdminCompetitionView(viewsets.ModelViewSet):
    serializer_class = AdminCompetitionSerializer
    http_method_names = ['get', 'put']

    def get_queryset(self):
        return Competition.objects.filter(id=self.request.user.competition.id)

    def get_permissions(self):
        if self.action in ['general_stats', 'list', 'retrieve']:
            return IsCompetitionAdmin(),
        else:
            return IsCompetitionSuperAdmin(),

    @action(detail=False, methods=['get'], name='General Comp Stats')
    def general_stats(self, request, *args, **kwargs):
        competition = self.request.user.competition
        ramadan_date = current_hijri_date
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
        stats['ramadan_date'] = current_hijri_date
        return Response({**stats})


class AdminInformationView(views.APIView):
    permission_classes = (IsCompetitionAdmin,)

    def get(self, request, *args, **kwargs):
        result = dict()
        user = self.request.user.competition_admins
        result['username'] = user.username
        result['first_name'] = user.first_name
        result['last_name'] = user.last_name
        result['is_super_admin'] = user.is_super_admin
        result['email'] = user.email
        result['phone_number'] = user.phone_number
        return Response({**result})
