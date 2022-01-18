from rest_framework import generics
from .models import *
from .serializers import *


class PointTemplates(generics.ListCreateAPIView):
    queryset = PointTemplate.objects.all()
    serializer_class = PointTemplateSerializer
    name = 'points-templates-list'

    filter_fields = (
        'competition_id',
    )


class CompGroupTemplate(generics.ListCreateAPIView):
    queryset = CompGroup.objects.all()
    serializer_class = CompGroupSerializer
    name = 'compgroup-list'

    filter_fields = (
        'competition_id',
    )
