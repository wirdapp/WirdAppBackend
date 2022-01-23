from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_condition import Or
from rest_framework import generics, permissions, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from compAdmin.models import CompAdmin
from core.permissions import IsCompetitionAdmin, IsCompetitionSuperAdmin
from .serializers import *


class PointRecords(viewsets.ModelViewSet):
    queryset = PointRecord.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointRecordSerializer
    name = 'points-record-list'


class StudentUserView(viewsets.ModelViewSet):
    permission_classes = [Or(IsCompetitionAdmin, IsAdminUser)]
    name = 'student-user-list'
    lookup_field = 'username'

    # model1.objects.get(pk=1).model2_set.all()  # Fetch me all model2 for this model1

    def get_queryset(self):
        user = self.request.user
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
                    return HttpResponse("")

    def get_serializer_class(self):
        user = self.request.user
        if self.action in ['create', 'list'] and (user is None or not isinstance(user, StudentUser)):
            return StudentUserSerializer
        elif self.action in ['update', 'partial_update']:
            if isinstance(user, StudentUser):
                return StudentUserStudentUpdateSerializer
            else:
                return StudentUserAdminUpdateSerializer

    # def get_permissions(self):
    #     if self.action in ['list']:
    #         return Or(IsAdminUser(), IsCompetitionAdmin()),
