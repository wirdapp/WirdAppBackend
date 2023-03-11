"""
Provides a set of pluggable permission policies.
"""
import logging
from collections.abc import Iterable

from rest_framework.permissions import BasePermission

from core import util

logger = logging.getLogger(__name__)


def person_role_in_contest(request, expected_roles):
    try:
        if not isinstance(expected_roles, Iterable):
            expected_roles = [expected_roles]
        current_contest = util.get_current_contest_dict(request)
        return bool(current_contest["role"] in expected_roles)
    except Exception as e:
        logger.error("Error while getting person role in contest", e)
        return False


class IsContestMember(BasePermission):
    def has_permission(self, request, view):
        return person_role_in_contest(request, [3, 2, 1])


class IsContestAdmin(BasePermission):
    def has_permission(self, request, view):
        return person_role_in_contest(request, [3, 2])


class IsContestSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return person_role_in_contest(request, [3])


class NoPermission(BasePermission):
    def has_permission(self, request, view):
        return False
