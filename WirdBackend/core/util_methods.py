from hijri_converter import Hijri

from core import models_helper
from core.models import ContestPerson


def get_today_date_hijri():
    return Hijri.today()


def get_username_from_session(request):
    if request.user.is_authenticated and "username" not in request.session:
        username = request.user.username
        request.session["username"] = username
        request.session.modified = True
    return request.session.get("username", "")


def get_current_contest_id_from_session(request):
    if "contest_id" not in request.session:
        username = get_username_from_session(request)
        contests = models_helper.get_person_contests(username)
        if contests.count() > 0:
            request.session["contest_id"] = contests[0].id
            request.session.modified = True
    return request.session["contest_id"]


def get_current_user_role_from_session(request):
    if "contest_role" not in request.session:
        username = get_username_from_session(request)
        contest_persons = models_helper.get_contest_person_objects(username)
        if contest_persons.count() > 0:
            request.session["contest_role"] = contest_persons[0].contest_role
            request.session.modified = True
    return request.session["contest_role"]


def is_person_role_in_contest(request, expected_roles):
    current_contest_role = get_current_user_role_from_session(request)
    return bool(current_contest_role in expected_roles)


def get_current_personcontest_object(request):
    contest = get_current_contest_id_from_session(request)
    username = get_username_from_session(request)
    return ContestPerson.objects.get(person__username=username, contest__id=contest)
