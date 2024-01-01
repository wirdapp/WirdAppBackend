"""
Provides a set of pluggable permission policies.
"""
import logging

from allauth.account.models import EmailAddress
from rest_framework.permissions import BasePermission, SAFE_METHODS

from core import util_methods
from core.util_methods import is_person_role_in_contest

logger = logging.getLogger(__name__)


class IsContestMember(BasePermission):
    def has_permission(self, request, view):
        return is_person_role_in_contest(request, [3, 2, 1, 0])


class IsContestAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_person_role_in_contest(request, [2, 1, 0])


class IsContestSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_person_role_in_contest(request, [1, 0])


class IsAuthenticatedAndReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.method in SAFE_METHODS)


class IsContestOwner(BasePermission):
    def has_permission(self, request, view):
        return is_person_role_in_contest(request, [0])


class NoPermission(BasePermission):
    def has_permission(self, request, view):
        return False


class EmailVerified(BasePermission):
    def has_permission(self, request, view):
        username = util_methods.get_username(request)
        return EmailAddress.objects.filter(user__username=username, verified=True).exists()
