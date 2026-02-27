"""
Export job helpers: validation, deduplication, rate limiting, background tasks.
"""
import logging
from datetime import timedelta

from django.utils import timezone

from admin_panel.models import ExportJob, ContestPersonGroup
from core import models_helper
from core.models import ContestPerson
from core.util_methods import get_dates_between_two_dates

logger = logging.getLogger('django')

MAX_ALL_MEMBERS_LIMIT = 5000

# ---------------------------------------------------------------------------
# Deduplication & rate-limit checks (called from the view)
# ---------------------------------------------------------------------------

def find_intersecting_date_range_job(requester, contest, start_date, end_date):
    """Return an existing job whose date range intersects the requested range,
    created by the same requester within the last hour, or None."""
    one_hour_ago = timezone.now() - timedelta(hours=1)
    return (
        ExportJob.objects
        .filter(
            requester=requester,
            contest=contest,
            created_at__gte=one_hour_ago,
        )
        .exclude(status=ExportJob.Status.FAILED)
        .filter(start_date__lte=end_date, end_date__gte=start_date)
        .order_by('-created_at')
        .first()
    )


def check_rate_limit(requester, contest):
    """Return True if the requester already submitted a job in the last hour."""
    one_hour_ago = timezone.now() - timedelta(hours=1)
    return (
        ExportJob.objects
        .filter(requester=requester, contest=contest, created_at__gte=one_hour_ago)
        .exclude(status=ExportJob.Status.FAILED)
        .exists()
    )


def find_duplicate_job(requester, contest, data):
    """Return a completed job with the same filters from the last 24h, or None."""
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    filters = {
        'requester': requester,
        'contest': contest,
        'start_date': data['start_date'],
        'end_date': data['end_date'],
        'status': ExportJob.Status.COMPLETED,
        'created_at__gte': twenty_four_hours_ago,
    }
    if data.get('group'):
        filters['group'] = data['group']
    elif data.get('member_ids'):
        filters['member_ids'] = data['member_ids']
    elif data.get('all_members'):
        filters['all_members'] = True

    return ExportJob.objects.filter(**filters).order_by('-created_at').first()


# ---------------------------------------------------------------------------
# Background tasks (dispatched via django-q async_task)
# ---------------------------------------------------------------------------

def process_export_job(job_id):
    """Resolve members, query points, build payload, save result."""
    try:
        job = ExportJob.objects.select_related('contest', 'requester', 'group').get(id=job_id)
    except ExportJob.DoesNotExist:
        logger.error(f"ExportJob {job_id} not found.")
        return

    job.status = ExportJob.Status.PROCESSING
    job.save(update_fields=['status'])

    try:
        members = _resolve_members(job)
        dates = get_dates_between_two_dates(job.start_date, job.end_date + timedelta(days=1))
        payload = _build_payload(members, dates)

        job.serialized_data = payload
        job.status = ExportJob.Status.COMPLETED
        job.save(update_fields=['serialized_data', 'status'])
        logger.info(f"ExportJob {job_id} completed with {len(payload['members'])} members.")
    except Exception as e:
        job.status = ExportJob.Status.FAILED
        job.error_message = str(e)
        job.save(update_fields=['status', 'error_message'])
        logger.exception(f"ExportJob {job_id} failed: {e}")


def cleanup_old_export_jobs():
    """Scheduled task: delete ExportJob records older than 24 hours."""
    cutoff = timezone.now() - timedelta(hours=24)
    deleted_count, _ = ExportJob.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"Cleaned up {deleted_count} old export jobs.")
    return deleted_count


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_members(job):
    """Return a queryset of ContestPerson based on the job's member selection."""
    base_qs = ContestPerson.objects.filter(
        contest=job.contest,
    ).select_related('person')

    if job.group_id:
        person_ids = (
            ContestPersonGroup.objects
            .filter(group=job.group)
            .values_list('contest_person_id', flat=True)
        )
        return base_qs.filter(id__in=person_ids)

    if job.member_ids:
        return base_qs.filter(id__in=job.member_ids)

    if job.all_members:
        return base_qs

    return base_qs


def _build_payload(members, dates):
    """Build the JSON payload suitable for Excel conversion."""
    date_strings = [d.strftime('%Y-%m-%d') for d in dates]
    members_data = []

    for member in members:
        points_by_date = (models_helper.get_person_points_by_date(member, dates, "-record_date")
                          .values_list('record_date', "points"))
        members_data.append({
            'username': str(member.person.username).strip(),
            'name': f"{member.person.first_name} {member.person.last_name}".strip(),
            'points_by_date': {d.strftime('%Y-%m-%d'): p for d, p in points_by_date},
        })

    return {'dates': date_strings, 'members': members_data}
