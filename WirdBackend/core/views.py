from rest_framework import viewsets, generics, serializers, mixins, permissions
from rest_framework.exceptions import APIException

from core.models import Contest, ContestPerson
from core.my_view import MyModelViewSet
from core.serializers import *


class ContestView(MyModelViewSet):
    serializer_class = ContestSerializer
    queryset = Contest.objects
    name = 'create-contest-view'
    non_member_allowed_methods = ["create"]
    member_allowed_methods = ['retrieve']
    admin_allowed_methods = ['retrieve', 'update', 'partial_update']
    filter_qs = False


# class ContestPersonView(MyModelViewSet):
#     serializer_class = ContestPersonSerializer
#     permission_classes = [IsAdminUser]
#     queryset = ContestPerson.objects
#     name = 'create-contest-person-relation-view'
#     member_allowed_methods = ['create', 'retrieve']

class SignUpView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        user_type = self.request.query_params.get("type", "participant")
        if user_type == "participant":
            return ParticipantSignupSerializer
        elif user_type == "creator":
            return CreatorSignupSerializer
