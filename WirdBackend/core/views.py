from rest_framework import viewsets, mixins, permissions

from core.my_view import MyModelViewSet
from core.serializers import *


class ContestView(MyModelViewSet):
    serializer_class = ContestSerializer
    queryset = Contest.objects
    name = 'create-contest-view'
    non_member_allowed_methods = ["create"]
    member_allowed_methods = ['retrieve']
    admin_allowed_methods = ['retrieve', 'update', 'partial_update']
    super_admin_allowed_methods = admin_allowed_methods


class SignUpView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        user_type = self.request.query_params.get("type", "participant")
        if user_type == "participant":
            return ParticipantSignupSerializer
        elif user_type == "creator":
            return CreatorSignupSerializer
