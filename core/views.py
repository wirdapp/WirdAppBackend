from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import *
from rest_framework.response import Response

from compAdmin.models import Competition
from core.permissions import NoPermission
from core.serializers import CompetitionReadOnlySerializer, TopStudentsSerializer
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
            return Response({**serializer.errors})
        serializer.update(user, serializer.validated_data)
        return Response({**serializer.data})


class CompetitionView(viewsets.ModelViewSet):
    serializer_class = CompetitionReadOnlySerializer
    name = 'competition-view'

    def get_queryset(self):
        if self.action == 'list':
            return Competition.objects.all()
        else:
            competition = self.request.user.competition
            return QuerySet(competition)

    def get_permissions(self):
        if self.action in ['list', 'list_top_students']:
            return AllowAny(),
        else:
            return NoPermission(),

    @action(detail=False, methods=['get'], name='List Top Students')
    def list_top_students(self, request, *args, **kwargs):
        competition = self.request.user.competition
        students = sorted(StudentUser.objects.filter(competition=competition), key=lambda st: st.total_points,
                          reverse=True)
        serializer = TopStudentsSerializer(students, many=True)
        return Response(serializer.data)
