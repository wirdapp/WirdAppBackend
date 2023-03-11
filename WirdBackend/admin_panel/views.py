from core.my_view import MyModelViewSet
from .serializers import *


class SectionView(MyModelViewSet):
    serializer_class = SectionSerializer
    name = 'section-list'
    lookup_field = 'id'
    queryset = Section.objects
    admin_allowed_methods = ['list', 'retrieve']


class PointTemplatesView(MyModelViewSet):
    serializer_class = PointTemplateSerializer
    name = 'points-templates-list'
    lookup_field = 'id'
    queryset = PointTemplate.objects
    admin_allowed_methods = ['list', 'retrieve']


class GroupView(MyModelViewSet):
    serializer_class = GroupSerializer
    name = 'contest-group-list'
    lookup_field = 'id'
    queryset = Group.objects
    admin_allowed_methods = ['list', 'update', 'partial_update', 'retrieve']
