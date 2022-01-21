from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions

from core.permissions import IsCompetitionAdmin
from .serializers import *


class PointRecords(generics.ListCreateAPIView):
    queryset = PointRecord.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PointRecordSerializer
    name = 'points-record-list'

    filter_fields = (
        'user',
        'ramadan_record_date',
    )


class StudentUserView(generics.ListCreateAPIView):
    queryset = StudentUser.objects.all()
    serializer_class = StudentUserSerializer
    permission_classes = [IsCompetitionAdmin]
    name = 'student-user-list'

    # def get_queryset(self):
    #     username = self.request.user.username
    #     admin = CompAdmin.objects.get(username=username)
    #     competition = admin.competition
    #     return StudentUser.objects.filter(competition__id=competition.id)
