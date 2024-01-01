from gettext import gettext

from hijri_converter import Hijri
from rest_framework import exceptions

from core import models_helper
from core.models import ContestPerson


def get_today_date_hijri():
    return Hijri.today()


def get_username(request):
    return request.user.username


def get_first_contest_id(username, raise_exception=False):
    contests = models_helper.get_person_contests(username)
    if contests.count() > 0:
        contest_id = contests.first().id
        return contest_id
    if raise_exception:
        raise exceptions.APIException("User is not enrolled in any contests")
    else:
        return None


def get_current_contest_id(request):
    contest_id = request.COOKIES.get('contest_id', None)
    if contest_id:
        return contest_id
    else:
        return get_first_contest_id(request.user.username, True)


def get_current_user_contest_role(request):
    contest_id = get_current_contest_id(request)
    username = get_username(request)
    try:
        return ContestPerson.objects.get(person__username=username, contest_id=contest_id).contest_role
    except ContestPerson.DoesNotExist:
        raise exceptions.APIException(gettext("error while getting user role in this contest"))


def is_person_role_in_contest(request, expected_roles):
    current_contest_role = get_current_user_contest_role(request)
    return bool(current_contest_role in expected_roles)
