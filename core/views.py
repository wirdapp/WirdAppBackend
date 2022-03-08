from django.db.models import QuerySet, Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import *
from rest_framework.response import Response

from compAdmin.models import Competition
from core.permissions import NoPermission
from core.serializers import CompetitionReadOnlySerializer, TopStudentsSerializer, CompetitionSerializer
from student.models import StudentUser


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChangePasswordViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['put'], name='Change Password')
    def change_password(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({**serializer.errors}, status=400)
        serializer.update(user, serializer.validated_data)
        return Response({**serializer.data})


class CompetitionView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompetitionReadOnlySerializer
    pagination_class = StandardResultsSetPagination
    name = 'competition-view'

    def get_queryset(self):
        if self.action == 'list':
            return Competition.objects.all()
        else:
            return Competition.objects.none()

    def get_permissions(self):
        if self.action == 'list':
            return AllowAny(),
        elif self.action == 'list_top_students':
            return IsAuthenticated(),
        else:
            return NoPermission(),

    @action(detail=False, name='List Top Students')
    def list_top_students(self, request, *args, **kwargs):
        competition = self.request.user.competition
        students = sorted(StudentUser.objects.filter(competition=competition), key=lambda st: st.total_points,
                          reverse=True)
        serializer = TopStudentsSerializer(students, many=True)
        return Response(serializer.data)


class CreateCompetitionView(viewsets.ModelViewSet):
    serializer_class = CompetitionSerializer
    permission_classes = [IsAdminUser]
    queryset = Competition.objects.all()
    name = 'create-competition-view'


def user_points_stats(user, stats_type):
    stats = dict()
    if stats_type == 'total_points_by_day':
        stats['total_points_by_day'] = user.competition_students.student_points.all() \
            .values('ramadan_record_date') \
            .annotate(total_day=Sum('point_total')).order_by('-ramadan_record_date')
    elif stats_type == 'total_points_by_type':
        stats['total_points_by_type'] = user.competition_students.student_points.all() \
            .values('point_template__label').annotate(total_point=Sum('point_total'))
    elif stats_type == 'daily_points_by_type':
        stats['daily_points_by_type'] = user.competition_students.student_points.all() \
            .values('point_template__label', 'ramadan_record_date') \
            .annotate(total_day=Sum('point_total')).order_by('-ramadan_record_date')
    else:
        return Response(
            'Please specify type as a query param [total_points_by_day, total_points_by_type, daily_points_by_type]')
    return Response(stats)
