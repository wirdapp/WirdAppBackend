"""
Provides a set of pluggable permission policies.
"""
from django.http import Http404

from rest_framework import exceptions
from rest_framework.permissions import BasePermission, IsAdminUser

from compAdmin.models import CompAdmin


class IsCompetitionAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            username = request.user.username
            comp_admin = CompAdmin.objects.get(username=username)
            competition = request.user.competition.id
            return bool(comp_admin.competition == competition or request.user.is_staff)
        except:
            return bool(request.user.is_staff)


class IsCompetitionSuperAdminOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            username = request.user.username
            comp_admin = CompAdmin.objects.get(username=username)
            return bool(comp_admin.is_super_admin or request.user.is_staff)
        except Exception:
            return bool(request.user.is_staff)


class IsGetRequest(BasePermission):
    def has_permission(self, request, view):
        return bool(request.method == "GET")
