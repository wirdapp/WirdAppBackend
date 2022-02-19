from rest_condition import Or
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.permissions import IsCompetitionSuperAdmin, IsCompetitionAdmin
from core.views import StandardResultsSetPagination, ChangePasswordViewSet
from student.serializers import PointRecordSerializer
from .serializers import *


class StudentView(ChangePasswordViewSet):
    pagination_class = StandardResultsSetPagination
    name = 'student-admin-view'
    lookup_field = 'username'

    def get_queryset(self):
        user = self.request.user
        competition = user.competition
        if user.is_staff:
            return StudentUser.objects.all()
        if hasattr(user, 'competition_admins'):
            admin = user.competition_admins
            if admin.is_super_admin:
                return StudentUser.objects.filter(competition=competition)
            else:
                return StudentUser.objects.filter(group__admin=user)

    def get_serializer_class(self):
        if self.action == "change_password":
            return StudentChangePasswordSerializer
        elif self.action == 'update_or_delete_point':
            return PointRecordSerializer
        elif self.action in ['update', 'partial_update', 'retrieve']:
            return StudentUserRetrieveSerializer
        else:
            return StudentUserSerializer

    def get_permissions(self):
        if self.action in ['list', 'update', 'partial_update', 'retrieve', 'change_password', 'update_or_delete_point',
                           None]:
            return Or(IsCompetitionAdmin(), IsAdminUser()),
        else:
            return Or(IsCompetitionSuperAdmin(), IsAdminUser()),

    @action(detail=True, methods=['put', 'delete', 'get'], name='Update or delete point')
    def update_or_delete_point(self, request, *args, **kwargs):
        point_id = request.query_params.get('id')
        if not point_id:
            return Response("Please specify point id", status=404)
        student = self.get_object()
        point = student.student_points.get(id=point_id)
        if self.request.method == 'GET':
            serializer = self.get_serializer(point)
            return Response({**serializer.data})
        elif self.request.method == 'PUT':
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({**serializer.errors})
            serializer.update(point, serializer.validated_data)
            return Response({**serializer.data})
        elif self.request.method == 'DELETE':
            point.delete()
            return Response("Deleted Successfully")
        else:
            return Response("Action is not supported", status=404)
