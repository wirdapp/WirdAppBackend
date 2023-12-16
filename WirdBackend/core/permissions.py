"""
Provides a set of pluggable permission policies.
"""
import logging
from collections.abc import Iterable

from rest_framework.permissions import BasePermission

from core import util_methods, models_helper
from allauth.account.admin import EmailAddress

from core.util_methods import person_role_in_contest

logger = logging.getLogger(__name__)


class IsContestMember(BasePermission):
    def has_permission(self, request, view):
        return person_role_in_contest(request, [3, 2, 1, 0])


class IsContestAdmin(BasePermission):
    def has_permission(self, request, view):
        return person_role_in_contest(request, [2, 1, 0])


class IsContestSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return person_role_in_contest(request, [1, 0])


class IsContestOwner(BasePermission):
    def has_permission(self, request, view):
        return person_role_in_contest(request, [0])


class NoPermission(BasePermission):
    def has_permission(self, request, view):
        return False


class EmailVerified(BasePermission):
    def has_permission(self, request, view):
        username = util_methods.get_username_from_session(request)
        return EmailAddress.objects.filter(user__username=username, verified=True).exists()


class IsGroupAdmin(BasePermission):
    # TODO: Support more variations
    def has_permission(self, request, view):
        contest_id = util_methods.get_current_contest(request)["id"]
        username = util_methods.get_username_from_session(request)
        group_id = view.kwargs["group_id"]
        return models_helper.get_person_managed_groups(username, contest_id).filter(id=group_id).exists()


class MemberBelongsToAdminGroups(BasePermission):
    def has_permission(self, request, view):
        # FIXME
        return True
