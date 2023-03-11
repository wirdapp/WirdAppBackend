from rest_framework.permissions import *

from core.models import Contest, ContestPerson
from core.my_view import MyModelViewSet
from core.serializers import ContestSerializer, ContestPersonSerializer


class ContestView(MyModelViewSet):
    serializer_class = ContestSerializer
    queryset = Contest.objects
    name = 'create-contest-view'
    non_member_allowed_methods = ["create"]
    member_allowed_methods = ['retrieve']
    admin_allowed_methods = ['retrieve', 'update', 'partial_update']
    filter_queryset = False


class ContestPersonView(MyModelViewSet):
    serializer_class = ContestPersonSerializer
    permission_classes = [IsAdminUser]
    queryset = ContestPerson.objects
    name = 'create-contest-person-relation-view'
    member_allowed_methods = ['create', 'retrieve']