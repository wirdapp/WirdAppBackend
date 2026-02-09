import logging

import pytz
from django.utils import timezone

from admin_panel.models import ContestCriterion
from core.models import Contest, ContestPerson
from member_panel.models import PointRecord
from notifications.notification_service import NotificationService

logger = logging.getLogger("django_q")


def send_daily_reminders():
    current_utc = timezone.now()
    target_hour = 22  # 10 PM

    # Find timezones where it's currently 10 PM
    target_timezones = set()
    for tz_name in pytz.common_timezones:
        tz = pytz.timezone(tz_name)
        local_time = current_utc.astimezone(tz)
        if local_time.hour == target_hour:
            target_timezones.add(tz_name)

    if not target_timezones:
        return 0

    today = current_utc.date()
    # Loop over active contests
    active_contests = Contest.objects.filter(
        readonly_mode=False,
        start_date__lte=today,
        end_date__gte=today,
    )

    for contest in active_contests:
        sent_count = 0
        # Get contestants in this contest whose users are in target timezones
        contest_persons = ContestPerson.objects.filter(
            contest=contest,
            person__timezone__in=target_timezones,
        ).select_related('person')

        criterion_count = ContestCriterion.objects.filter(contest=contest).count()
        for contest_person in contest_persons:
            records_count = PointRecord.objects.filter(person=contest_person, record_date=today).count()
            submitted_points_ratio = records_count / criterion_count if criterion_count else 0

            if submitted_points_ratio < 0.75:
                try:
                    success = NotificationService.send_daily_reminder(contest_person)
                    if success: sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending daily reminder for user {contest_person.person.username}: {e}")

        logger.info(f"Sent {sent_count} daily reminders for contest {contest.name}.")


def send_admin_notification_task(notification):
    try:
        NotificationService.send_admin_notification(notification)
        logger.info(f"Sent admin notification: {notification} at {notification.sent_at}")
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")
