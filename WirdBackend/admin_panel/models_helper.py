from collections import defaultdict

from member_panel.models import PointRecord


def get_bulk_member_results(contest, members, start_date, end_date):
    """
    Fetch and aggregate point records for multiple members across a date range.

    Returns a dict with:
      - criteria: list of unique criteria encountered
      - members: list of per-member result dicts
    """
    records = (
        PointRecord.objects
        .filter(
            person__contest=contest,
            person__in=members,
            record_date__range=(start_date, end_date),
        )
        .select_related(
            'contest_criterion',
            'contest_criterion__section',
            'person',
            'person__person',
        )
    )

    criteria_map = {}
    member_data = {}

    for record in records:
        person_id = str(record.person.id)
        criterion_id = str(record.contest_criterion.id)
        date_str = record.record_date.strftime("%Y-%m-%d")
        points = record.point_total

        # Track unique criteria
        if criterion_id not in criteria_map:
            criterion = record.contest_criterion
            criteria_map[criterion_id] = {
                "id": criterion_id,
                "label": criterion.label,
                "section_label": criterion.section.label,
                "max_points": criterion.points,
            }

        # Initialize member entry if needed
        if person_id not in member_data:
            person = record.person.person
            member_data[person_id] = {
                "id": person_id,
                "name": f"{person.first_name} {person.last_name}".strip(),
                "username": person.username,
                "total_points": 0,
                "total_submissions": 0,
                "daily_points": defaultdict(int),
                "criterion_daily_points": defaultdict(lambda: defaultdict(int)),
            }

        entry = member_data[person_id]
        entry["total_points"] += points
        entry["total_submissions"] += 1
        entry["daily_points"][date_str] += points
        entry["criterion_daily_points"][criterion_id][date_str] += points

    # Convert defaultdicts to plain dicts for serialization
    members_result = []
    for member in members:
        person_id = str(member.id)
        if person_id in member_data:
            entry = member_data[person_id]
            members_result.append({
                "id": entry["id"],
                "name": entry["name"],
                "username": entry["username"],
                "total_points": entry["total_points"],
                "total_submissions": entry["total_submissions"],
                "daily_points": dict(entry["daily_points"]),
                "criterion_daily_points": {
                    crit_id: dict(dates)
                    for crit_id, dates in entry["criterion_daily_points"].items()
                },
            })
        else:
            # Member with no records in the date range
            person = member.person
            members_result.append({
                "id": person_id,
                "name": f"{person.first_name} {person.last_name}".strip(),
                "username": person.username,
                "total_points": 0,
                "total_submissions": 0,
                "daily_points": {},
                "criterion_daily_points": {},
            })

    return {
        "criteria": list(criteria_map.values()),
        "members": members_result,
    }
