import hashlib

from hijri_converter import Hijri
from rest_framework.response import Response

from core import models_helper
from core.models import Contest, ContestPerson
from rest_framework.decorators import action


def hash_multiple_values(*args):
    return hashlib.md5(("".join(args)).encode('utf-8')).hexdigest()


def get_today_date_hijri():
    return Hijri.today()


def destroy(instance):
    instance.is_active = False
    instance.save()
    return Response(status=204)


def get_username_from_session(request):
    if "username" not in request.session:
        username = request.user.username
        request.session["username"] = username
        request.session.modified = True
    return request.session.get("username", "")


def get_current_contest(request):
    if "contest_id" not in request.session:
        username = get_username_from_session(request)
        contests = models_helper.get_person_contests_ids_and_roles(username)
        if contests.count() > 0:
            request.session["contest_id"] = contests[0][0].hex
            request.session["contest_role"] = contests[0][1]
            request.session.modified = True
    return {"id": request.session.get("contest_id", ""), "role": request.session.get("contest_role", "")}


def person_role_in_contest(request, expected_roles):
    current_contest = get_current_contest(request)
    return bool(current_contest["role"] in expected_roles)


def get_current_contest_object(request):
    username = get_username_from_session(request)
    current_contest = get_current_contest(request)
    if current_contest:
        return Contest.objects.get(id=current_contest["id"])
    else:
        return models_helper.get_person_contests_queryset(username).first()


def get_current_personcontest_object(request):
    contest = get_current_contest(request)["id"]
    username = get_username_from_session(request)
    return ContestPerson.objects.get(person__username=username, contest__id=contest)
