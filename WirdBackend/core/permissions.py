"""
Provides a set of pluggable permission policies.
"""
from collections.abc import Iterable

from rest_framework.permissions import BasePermission

from core import util


def person_role_in_contest(request, expected_roles):
    if not isinstance(expected_roles, Iterable):
        expected_roles = [expected_roles]
    current_contest = util.get_current_contest_dict(request)
    return bool(current_contest["current_contest_role"] in expected_roles)


# TODO: Remove is_staff part from the conditions
class IsContestMember(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_staff or person_role_in_contest(request, [3, 2, 1])
        except:
            return False


class IsContestAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_staff or person_role_in_contest(request, [3, 2])
        except:
            return False


class IsContestSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            return person_role_in_contest(request, [3])
        except:
            return False


class NoPermission(BasePermission):
    def has_permission(self, request, view):
        return False
