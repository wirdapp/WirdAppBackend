from member_panel.models import PointRecord

from core.util_methods import get_current_contest_person, get_current_contest


def get_member_point_records(request):
    person = get_current_contest_person(request)
    contest_id = get_current_contest(request)
    return PointRecord.objects.filter(person__id=person.id, contest__id=contest_id)