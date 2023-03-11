from django.db.models import Sum
from rest_condition import Or
from rest_framework import viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core import util
from core.permissions import IsCompetitionSuperAdmin, IsCompetitionAdmin
from core.util import current_hijri_date, get_from_cache, save_to_cache
from core.views import ChangePasswordViewSet
from student.models import PointRecord
from .serializers import *


class SectionView(viewsets.ModelViewSet):
    permission_classes = [Or(IsCompetitionSuperAdmin, IsAdminUser)]
    serializer_class = SectionSerializer
    name = 'section-list'
    lookup_field = 'id'

    def get_queryset(self):
        comp = self.request.user.competition
        return comp.competition_sections.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return Or(IsAdminUser(), IsCompetitionAdmin()),
        else:
            return Or(IsAdminUser(), IsCompetitionSuperAdmin()),


class PointTemplatesView(viewsets.ModelViewSet):
    serializer_class = PointTemplateSerializer
    name = 'points-templates-list'
    lookup_field = 'id'

    def get_queryset(self):
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
    name = 'competition-admin-api'
    lookup_field = 'username'

    def destroy(self, request, *args, **kwargs):
        return util.destroy(self.get_object())

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'competition_admins'):
            admin = user.competition_admins
            if admin.is_super_admin:
                return CompAdmin.objects.filter(competition__id=admin.competition_id, is_active=True)
            else:
                return CompAdmin.objects.filter(username=admin.username, is_active=True)

    def get_permissions(self):
        if action in ['update', 'partial_update', 'retrieve']:
            return Or(IsCompetitionAdmin(), IsAdminUser)
        else:
            return Or(IsCompetitionSuperAdmin(), IsAdminUser),

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
        return Competition.objects.filter(id=self.request.user.competition_id)

    def get_permissions(self):
        if self.action in ['general_stats', 'list', 'retrieve']:
            return IsCompetitionAdmin(),
        else:
            return IsCompetitionSuperAdmin(),

    @action(detail=False, methods=['get'], name='General Comp Stats')
    def general_stats(self, request, *args, **kwargs):
        competition_id = self.request.user.competition_id
        ramadan_date = current_hijri_date - 1
        key = f'general_stats_{competition_id}_{ramadan_date}'
        res = get_from_cache(key)
        if res:
            return Response({**res})
        stats = dict()
        top_on_day = StudentUser.objects.filter(competition__id=competition_id) \
            .values('username', 'first_name', 'last_name', 'student_points__point_total') \
            .filter(student_points__ramadan_record_date=ramadan_date) \
            .annotate(points_per_day=Sum('student_points__point_total')) \
            .order_by('-points_per_day').first()

        stats['top_student_last_day'] = top_on_day
        stats['top_ramadan_day'] = PointRecord.objects.filter(point_template__competition__id=competition_id) \
            .values('ramadan_record_date') \
            .annotate(total_day=Sum('point_total')).order_by('-total_day').first()
        stats['students_count'] = StudentUser.objects.filter(competition__id=competition_id).count()
        stats['ramadan_date'] = current_hijri_date
        save_to_cache(key, stats, timeout=600)
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
