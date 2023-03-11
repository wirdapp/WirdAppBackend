from rest_condition import Or
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core import util
from core.permissions import IsCompetitionSuperAdmin, IsCompetitionAdmin
from core.views import ChangePasswordViewSet, user_points_stats
from .serializers import *
from .student_serializers import StudentUserSerializer, StudentUserRetrieveSerializer, StudentChangePasswordSerializer, \
    UpdatePointRecordSerializer


class StudentView(ChangePasswordViewSet):
    name = 'student-admin-view'
    lookup_field = 'username'
    lookup_value_regex = '[\w.@+-]+'
    http_method_names = ['put', 'delete', 'get']

    def destroy(self, request, *args, **kwargs):
        return util.destroy(self.get_object())

    def get_queryset(self):
        user = self.request.user
        competition = user.competition_id
        if hasattr(user, 'competition_admins'):
            admin = user.competition_admins
            if admin.is_super_admin:
                return StudentUser.objects.filter(competition__id=competition, is_active=True)
            else:
                return StudentUser.objects.filter(group__admin__username=user.username, is_active=True)

    def get_serializer_class(self):
        if self.action == "change_password":
            return StudentChangePasswordSerializer
        elif self.action in ['update_or_delete_point', 'get_user_input_records']:
            return UpdatePointRecordSerializer
        elif self.action in ['update', 'partial_update', 'retrieve']:
            return StudentUserRetrieveSerializer
        else:
            return StudentUserSerializer

    def get_permissions(self):
        if self.action in ['points_stats', 'list', 'update', 'partial_update', 'retrieve', 'change_password',
                           'update_or_delete_point']:
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
            data = request.data.copy()
            data.update({'student': student})
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                return Response({**serializer.errors}, status=400)
            serializer.update(point, serializer.validated_data)
            return Response({**serializer.data})
        elif self.request.method == 'DELETE':
            point.delete()
            return Response("Deleted Successfully", status=204)
        else:
            return Response("Action is not supported", status=404)

    @action(detail=True, methods=['get'], name='Get User Input Records')
    def get_user_input_records(self, request, *args, **kwargs):
        user = self.get_object()
        date = request.query_params['date'] if 'date' in request.query_params else util.current_hijri_date
        points = user.student_points.filter(point_template__form_type='oth', point_scored_units=-1,
                                            ramadan_record_date=date)
        serializer = self.get_serializer(points, many=True)
        return Response(serializer.data)

    @action(detail=True, name='Point Scores Stats')
    def points_stats(self, request, *args, **kwargs):
        student = self.get_object()
        stats_type = request.query_params['type'] if 'type' in request.query_params else ''
        date = request.query_params['date'] if 'date' in request.query_params else None
        return user_points_stats(student, stats_type, date)
