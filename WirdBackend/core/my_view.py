from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from core import util
from core.permissions import IsContestAdmin, IsContestSuperAdmin


class MyModelViewSet(ModelViewSet):
    admin_allowed_methods = ['retrieve', 'list', 'create', 'update', 'partial_update']
    member_allowed_methods = []
    non_member_allowed_methods = []
    filter_qs = True

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.filter_qs:
            contest = util.get_current_contest_dict(self.request)
            queryset = queryset.filter(contest__id=contest["id"])
        return queryset

    def get_permissions(self):
        if self.action in self.admin_allowed_methods:
            return IsContestAdmin(),
        elif self.action in self.member_allowed_methods:
            return permissions.IsAuthenticated(),
        elif self.action in self.non_member_allowed_methods:
            return permissions.AllowAny(),
        else:
            return IsContestSuperAdmin(),
