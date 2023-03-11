from django.contrib.auth import password_validation
from django.db.models import Sum
from rest_framework import viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import *
from rest_framework.response import Response

from compAdmin.models import Competition
from core.models import GeneralUser
from core.permissions import IsCompetitionAdmin
from core.serializers import CompetitionReadOnlySerializer, TopStudentsSerializer, CompetitionSerializer
from core.util import get_from_cache, save_to_cache
from student.models import StudentUser


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
            return IsCompetitionAdmin(),

    @action(detail=False, name='List Top Students')
    def list_top_students(self, request, *args, **kwargs):
        competition = self.request.user.competition_id
        key = f'list_top_students_{competition}'
        res = get_from_cache(key)
        if res:
            return Response(res)
        students = StudentUser.objects.filter(competition__id=competition)
        serializer = TopStudentsSerializer(students, many=True)
        sorted_res = sorted(serializer.data, key=lambda x: x['total_points'], reverse=True)
        save_to_cache(key, sorted_res, timeout=600)
        return Response(sorted_res)


class CreateCompetitionView(viewsets.ModelViewSet):
    serializer_class = CompetitionSerializer
    permission_classes = [IsAdminUser]
    queryset = Competition.objects.all()
    name = 'create-competition-view'


def user_points_stats(user, stats_type, date):
    stats = dict()
    key = f'user_points_stats_{user}_{stats_type}_{date}'
    res = get_from_cache(key)
    if res:
        return Response(res)
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
            'Please specify type as a query param:'
            '?type=[total_points_by_day, total_points_by_type, daily_points_by_type]', status=400)
    if date:
        stats[stats_type] = stats.get(stats_type).filter(ramadan_record_date=date)
    save_to_cache(key, stats, timeout=600)
    return Response(stats)


class CheckUserNamePasswordView(views.APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request, *args, **kwargs):
        username = request.data['username']
        password = request.data['password']
        result = dict()
        result['username_ok'] = not GeneralUser.objects.filter(username=username).exists()
        result['password_ok'] = True
        try:
            password_validation.validate_password(password, GeneralUser(username=username))
        except Exception as ve:
            result['password_ok'] = False
            result['password_errors'] = list(ve)
        return Response({**result})
