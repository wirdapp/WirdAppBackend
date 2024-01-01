from gettext import gettext

from hijri_converter import Hijri
from rest_framework import exceptions

from core.models import ContestPerson


def get_today_date_hijri():
    return Hijri.today()


def get_username(request):
    return request.user.username


def get_current_contest_id(request):
    return request.parser_context.get("kwargs").get("contest_id")


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
