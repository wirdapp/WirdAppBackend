from collections.abc import Iterable

from admin_panel.models import PointTemplate, Section
from core.models import ContestPerson, Contest, Person, Group, ContestPersonGroups


def get_contest_people(contest_id, contest_role=(1, 2, 3)):
    return ContestPerson.objects.filter(contest__id=contest_id, contest_role__in=contest_role)


def get_person_contests_ids_and_roles(username, contest_role=(0, 1, 2, 3, 4, 5)):
    queryset = ContestPerson.objects.filter(person__username=username, contest_role__in=contest_role) \
        .values_list("contest__id", "contest_role")

    return queryset


def get_person_contests_queryset(username, contest_role=(0, 1, 2, 3)):
    contest_ids = get_person_contests_ids_and_roles(username, contest_role)
    contest_ids = [c[0] for c in contest_ids]
    return Contest.objects.filter(id__in=contest_ids)


def get_person_managed_groups(username, contest_id):
    persons = ContestPerson.objects.filter(person__username=username, contest_id=contest_id)
    is_super_admin = persons.filter(contest_role=3).exists()
    is_admin = persons.filter(contest_role=2).exists()
    if is_super_admin:
        return Group.objects.filter(contest__id=contest_id)
    elif is_admin:
        group_ids = ContestPersonGroups.objects.filter(contest_person__person__username=username) \
            .filter(group_role=2).values_list("group__id", flat=True)
        return Group.objects.filter(id__in=group_ids)


def get_group_admins_person_objects(group_id):
    person_ids = ContestPersonGroups.objects.filter(group__id=group_id, group_role=2) \
        .values_list('contest_person__person__id', flat=True)
    return Person.objects.filter(id__in=person_ids)


def get_group_members_contest_person_ids(group_id):
    return ContestPersonGroups.objects.filter(group__id=group_id, group_role=1) \
        .values_list('contest_person_id', flat=True)


def get_group_members_person_objects(group_id):
    person_ids = ContestPersonGroups.objects.filter(group__id=group_id, group_role=1) \
        .values_list('contest_person__person__id', flat=True)
    return Person.objects.filter(id__in=person_ids)


def get_contest_point_templates(contest_id):
    return PointTemplate.objects.filter(contest__id=contest_id)


def get_contest_sections(contest_id):
    return Section.objects.filter(contest__id=contest_id)


def get_contest_groups(contest_id):
    return Group.objects.filter(contest__id=contest_id)
