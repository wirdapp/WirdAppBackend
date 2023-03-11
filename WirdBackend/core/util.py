import hashlib

from django.core.cache import cache
from hijri_converter import Hijri
from rest_framework.response import Response

from core.models import ContestPerson


def hash_multiple_values(*args):
    return hashlib.md5(("".join(args)).encode('utf-8')).hexdigest()


def get_today_date_hijri():
    return Hijri.today()


def destroy(instance):
    instance.is_active = False
    instance.save()
    return Response(status=204)


def get_user_contest_person_objects(request):
    username = request.user.username
    key = hash_multiple_values(username)
    objects = cache.get(key)
    if not objects:
        objects = ContestPerson.objects.filter(person__username=username).prefetch_related("contest", "person", "group")
        cache.set(key, objects, 60)
    return objects


def get_user_contests(request):
    return [(p.contest.id, p.contest_role) for p in get_user_contest_person_objects(request)]


def get_current_contest_dict(request):
    if not ("current_contest_id" in request.session and "current_contest_role" in request.session):
        contests = get_user_contests(request)
        if len(contests) > 0:
            request.session["current_contest_id"] = contests[0][0]
            request.session["current_contest_role"] = contests[0][1]
        else:
            raise Exception("User Have No Contests!")
    return {"id": request.session["current_contest_id"], "role": request.session["current_contest_role"]}


def get_contest_person_object(request):
    contest = get_current_contest_dict(request)
    contest_person_objects = get_user_contest_person_objects(request)
    return contest_person_objects.filter(contest__id=contest["id"])[0]


def get_contest(request):
    contest_person_object = get_contest_person_object(request)
    return contest_person_object.contest
