from rest_condition import And
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsContestAdmin, IsContestSuperAdmin, NoPermission


class MyModelViewSet(ModelViewSet):
    super_admin_allowed_methods = ['retrieve', 'list', 'create', 'update', 'partial_update']
    admin_allowed_methods = ['retrieve', 'list', 'create', 'update', 'partial_update']
    member_allowed_methods = []
    non_member_allowed_methods = []
    filter_qs = True

    def get_permissions(self):
        if True:
            return AllowAny(),
        if self.action in self.non_member_allowed_methods:
            return AllowAny(),
        elif self.action in self.member_allowed_methods:
            return IsAuthenticated(),
        elif self.action in self.admin_allowed_methods:
            return And(IsAuthenticated(), IsContestAdmin()),
        elif self.action in self.super_admin_allowed_methods:
            return And(IsAuthenticated(), IsContestSuperAdmin()),
        else:
            return NoPermission(),
