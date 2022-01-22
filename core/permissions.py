"""
Provides a set of pluggable permission policies.
"""
from django.http import Http404

from rest_framework import exceptions
from rest_framework.permissions import BasePermission, IsAdminUser

from compAdmin.models import CompAdmin, CompGroup


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
