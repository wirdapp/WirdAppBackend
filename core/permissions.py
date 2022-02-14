"""
Provides a set of pluggable permission policies.
"""

from rest_framework.permissions import BasePermission

from compAdmin.models import CompAdmin


class IsCompetitionAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            username = request.user.username
            comp_admin = CompAdmin.objects.get(username=username)
            competition = request.user.competition
            return bool(comp_admin.competition == competition)
        except:
            return False


class IsCompetitionSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            username = request.user.username
            comp_admin = CompAdmin.objects.get(username=username)
            competition = request.user.competition
            return bool(comp_admin.competition == competition and comp_admin.is_super_admin)
        except:
            return False


class NoPermission(BasePermission):
    def has_permission(self, request, view):
        return False
