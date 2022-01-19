"""
Provides a set of pluggable permission policies.
"""
from django.http import Http404

from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from compAdmin.models import CompAdmin


class IsCompetitionAdmin(BasePermission):
    def has_permission(self, request, view):
        username = request.user.username
        comp_admin = CompAdmin.objects.get(username=username)
        competition = request.user.competition.id
        return bool(comp_admin.competition == competition)


class IsGetRequest(BasePermission):
    def has_permission(self, request, view):
        return bool(request.method == "GET")
