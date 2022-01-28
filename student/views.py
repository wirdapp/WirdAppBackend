# Create your views here.
from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from rest_condition import Or
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated

from core.permissions import IsCompetitionAdmin
from core.views import StandardResultsSetPagination
from .serializers import *


class PointRecordsView(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointRecordSerializer
    name = 'points-record-list'
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'competition_students'):
            return user.competition_students.student_points.all()
        else:
            return PointRecord.objects.none()


class StudentUserView(viewsets.ModelViewSet):
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
            return QuerySet(user.competition_students)
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
