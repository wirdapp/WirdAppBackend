import hashlib
from gettext import gettext

from hijri_converter import Hijri
from rest_framework.response import Response

from core import models_helper
from core.models import Contest


def hash_multiple_values(*args):
    return hashlib.md5(("".join(args)).encode('utf-8')).hexdigest()


def get_today_date_hijri():
    return Hijri.today()


def destroy(instance):
    instance.is_active = False
    instance.save()
    return Response(status=204)


def get_username_from_session(request):
    if not "username" in request.session or request.session['username'] == '':
        username = request.user.username
        request.session["username"] = username
    return request.session["username"]


def get_current_contest_dict(request):
    if not ("current_contest_id" in request.session and "current_contest_role" in request.session):
        username = get_username_from_session(request)
        contests = models_helper.get_person_contests_ids_and_roles(username)
        if len(contests) > 0:
            request.session["current_contest_id"] = contests[0][0].hex
            request.session["current_contest_role"] = contests[0][1]
        else:
            raise Exception(gettext("user has no contests"))
    return {"id": request.session["current_contest_id"], "role": request.session["current_contest_role"]}


def update_current_contest_dict(request, contest_id):
    username = get_username_from_session(request)
    contest = models_helper.get_person_contests_ids_and_roles(username).get(contest__id=contest_id)
    request.session["current_contest_id"] = contest[0].hex
    request.session["current_contest_role"] = contest[1]


def get_current_contest_object(request):
    current_contest_id = get_current_contest_dict(request)["id"]
    return Contest.objects.get(id=current_contest_id)
