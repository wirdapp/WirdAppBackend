from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from rest_condition import Or
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated

from core.permissions import IsCompetitionAdmin
from core.views import StandardResultsSetPagination, ChangePasswordSerializer
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
        date = self.request.query_params.get('ramadan_record_date', 0)
        student_username = self.request.query_params.get('student_username', '0')
        if hasattr(user, 'competition_students'):
            return user.competition_students.student_points.filter(ramadan_record_date=date)
        elif hasattr(user, 'competition_admins'):
            students = StudentUserView(context={'request': self.request}, request=self.request).get_queryset()
            points = students.get(username=student_username).student_points().filter(ramadan_record_date=date)
            return points


class StudentUserView(ChangePasswordSerializer):
    pagination_class = StandardResultsSetPagination
    name = 'student-user-list'
    lookup_field = 'username'

    def get_queryset(self):
        user = self.request.user
        competition = user.competition
        if isinstance(user, AnonymousUser):
            return StudentUser.objects.none()
        if user.is_staff:
            return StudentUser.objects.all()
        if hasattr(user, 'competition_students'):
            return QuerySet(user.competition_students).filter(username=user.username)
        if hasattr(user, 'competition_admins'):
            admin = user.competition_admins
            if admin.is_super_admin:
                return competition.competition_students.all()
            else:
                try:
                    groups = competition.competition_groups.filter(admin=admin)
                    res = StudentUser.objects.none()
                    merge_sets = lambda x, y: x | y
                    for g in groups:
                        res = merge_sets(res, g.group_students.all())
                    return res
                except:
                    return StudentUser.objects.none()

    def get_serializer_class(self):
        if self.action in ['create', 'list']:
            return StudentUserSerializer
        elif self.action == "change_password":
            return StudentUserUpdatePasswordSerializer
        elif self.action in ['update', 'partial_update', 'retrieve']:
            user = self.request.user
            if hasattr(user, 'competition_students'):
                return StudentUserStudentUpdateSerializer
            else:
                return StudentUserAdminUpdateSerializer

    def get_permissions(self):
        if self.action == 'create':
            return AllowAny(),
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return IsAuthenticated(),
        else:
            return Or(IsAdminUser(), IsCompetitionAdmin()),
