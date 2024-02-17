from datetime import timedelta, datetime

from django.shortcuts import get_object_or_404
from hijri_converter import Hijri
from rest_framework import exceptions

from core.models import ContestPerson, Contest


def get_dates_between_two_dates(start, end):
    if isinstance(start, str):
        start = datetime.strptime(start, "%Y-%m-%d").date()
    if isinstance(end, str):
        end = datetime.strptime(end, "%Y-%m-%d").date()
    return [start + timedelta(days=d) for d in range((end - start).days)]


def get_today_date_hijri():
    return Hijri.today()


def get_username(request):
    return request.user.username


def get_current_contest(request):
    contest_id = ""
    if hasattr(request, "parser_context"):
        contest_id = request.parser_context.get("kwargs").get("contest_id")
    elif hasattr(request, "kwargs"):
        contest_id = request.kwargs.get("contest_id")
    return get_object_or_404(Contest, id=contest_id)


def get_current_user_contest_role(request):
    contest = get_current_contest(request)
    username = get_username(request)
    try:
        return ContestPerson.objects.get(person__username=username, contest=contest).contest_role
    except Exception as e:
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(detail=str(e))


def get_current_contest_person(request):
    contest_id = get_current_contest(request)
    username = get_username(request)
    try:
        return ContestPerson.objects.get(person__username=username, contest_id=contest_id)
    except Exception as e:
        if request.authenticators and not request.successful_authenticator:
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(detail=str(e))


def is_person_role_in_contest(request, expected_roles):
    current_contest_role = get_current_user_contest_role(request)
    return bool(current_contest_role in expected_roles)


def get_contest_and_request_related_start_and_end_date(request, contest):
    contest_start_date = contest.start_date
    contest_end_date = contest.end_date
    start_date = max(request.query_params.get("start_date", contest_start_date), contest_start_date)
    end_date = min(datetime.today().date() + timedelta(days=1), request.query_params.get("end_date", contest_end_date))
    return start_date, end_date
