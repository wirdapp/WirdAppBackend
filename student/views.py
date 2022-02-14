from rest_framework import permissions, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.permissions import NoPermission
from core.views import StandardResultsSetPagination
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
        date = self.request.query_params.get('ramadan_record_date', 1)
        if hasattr(user, 'competition_students'):
            return StudentUser.objects.get(username=user.username).student_points.filter(ramadan_record_date=date)
        else:
            return PointRecord.objects.none()


class StudentUserView(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    name = 'student-user-list'

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'competition_students'):
            return StudentUser.objects.get(username=user.username)
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
