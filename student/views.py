from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import *
from .serializers import *


class PointRecords(generics.ListCreateAPIView):
    queryset = PointRecord.objects.all()
    serializer_class = PointRecordSerializer
    name = 'points-record-list'

    filter_fields = (
        'user',
        'ramadan_record_date',
    )


class StudentUser(generics.ListCreateAPIView):
    queryset = StudentUser.objects.all()
    serializer_class = StudentUserSerializer
    name = 'student-user-list'

    filter_fields = (
        'competition',
        'group',
    )
