from django.contrib.auth.models import AnonymousUser

# Create your views here.
from django.db.models import QuerySet
from rest_condition import Or
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated

from compAdmin.models import CompAdmin
from core.permissions import IsCompetitionSuperAdmin
from .serializers import *


class PointRecordsView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointRecordSerializer
    name = 'points-record-list'
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, StudentUser):
            return user.student_points
        else:
            return PointRecord.objects.none()


class StudentUserView(viewsets.ModelViewSet):
    name = 'student-user-list'
    lookup_field = 'username'

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return StudentUser.objects.none()
        competition = user.competition
        if user.is_staff:
            return StudentUser.objects.all()
        if isinstance(user, CompAdmin) and user.is_super_admin:
            if user.is_super_admin:
                return competition.generaluser_set.filter(competition_students=True)
            else:
                try:
                    return competition.competition_groups.filter(admin=user).first().group_students
                except:
                    return StudentUser.objects.none()
        if user.competition_students:
            return QuerySet(user.competition_students)

    def get_serializer_class(self):
        user = self.request.user
        if self.action in ['create', 'list'] and (user is None or not isinstance(user, StudentUser)):
            return StudentUserSerializer
        elif self.action in ['update', 'partial_update', 'retrieve']:
            if user.competition_students:
                return StudentUserStudentUpdateSerializer
            else:
                return StudentUserAdminUpdateSerializer

    def get_permissions(self):
        if self.action == 'create':
            return AllowAny(),
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return IsAuthenticated(),
        else:
            return Or(IsAdminUser(), IsCompetitionSuperAdmin()),
