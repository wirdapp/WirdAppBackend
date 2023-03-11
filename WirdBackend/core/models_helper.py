from collections.abc import Iterable
from functools import cache

from core.models import ContestPerson


@cache
def get_contest_students(contest_id):
    return ContestPerson.objects.filter(contest_id=contest_id, contest_status=1, group_status=1).values('person')


def get_person_contests(username, contest_status):
    if not isinstance(contest_status, Iterable):
        contest_status = [contest_status]

    return ContestPerson.objects.filter(person__username=username, contest_status__in=contest_status) \
        .values('contest')


def get_person_managed_contests(username):
    return get_person_contests(username, [2, 3])


def get_person_contest_ids(username, contest_status):
    return ContestPerson.objects.filter(person__username=username, contest_status=contest_status) \
        .values_list('contest__id')


def get_person_managed_groups(username, contest_id):
    return ContestPerson.objects.filter(person__username=username, contest_id=contest_id, contest_status__in=[2, 3],
                                        group_status=2).values('group')


def get_group_admins(group_id):
    return ContestPerson.objects.filter(group__id=group_id, contest_status__in=[2, 3], group_status=2).values('person')


def get_group_students(group_id):
    return ContestPerson.objects.filter(group__id=group_id, contest_status=1, group_status=1).values('person')
