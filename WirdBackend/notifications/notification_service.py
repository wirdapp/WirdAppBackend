from typing import List

from django.utils import timezone

from core.models import ContestPerson
from notifications.fcm_service import FCMService, NotificationPayload
from notifications.models import UserDevice, Notification, NotificationLog


class NotificationService:
    """Service for handling all notification logic."""

    @staticmethod
    def get_user_active_tokens(user) -> List[str]:
        """Get all active FCM tokens for a user."""
        return list(
            UserDevice.objects.filter(
                user=user,
            ).values_list('fcm_token', flat=True)
        )

    @staticmethod
    def delete_invalid_tokens(tokens: List[str]):
        """Mark invalid tokens as inactive."""
        if tokens:
            UserDevice.objects.filter(fcm_token__in=tokens).delete()

    @classmethod
    def send_daily_reminder(cls, contest_person):
        person = contest_person.person
        tokens = cls.get_user_active_tokens(person)
        if not tokens:
            return False

        language = getattr(person, 'language', 'ar')
        name = person.first_name or person.username
        contest = contest_person.contest
        # Localized messages
        messages = {
            'en': {
                'title': 'Daily Reminder: Submit your points!',
                'body': f"Salam Alaiukm, {name}.\nDon't forget to submit your points for {contest.name}!",
            },
            'ar': {
                'title': 'تذكير يومي: سجّل نقاطك!',
                'body': f"السلام عليكم يا {name}.\nلا تنسَ تسجيل نقاطك لمسابقة {contest.name}!",
            },
        }

        msg = messages.get(language, messages['ar'])
        payload = NotificationPayload(
            title=msg['title'],
            body=msg['body'],
            data={
                'type': 'daily_reminder',
                'competition_id': str(contest.id),
            }
        )

        result = FCMService.send_to_tokens(tokens, payload)

        # Delete invalid tokens
        cls.delete_invalid_tokens(result['invalid_tokens'])

        # Log the notification
        NotificationLog.objects.create(
            receiver=user,
            notification_type='daily_reminder',
            success=result['success'] > 0,
            error_message=f"Success: {result['success']}, Failed: {result['failure']}"
        )

        return result['success'] > 0

    @classmethod
    def send_admin_notification(cls, admin_notification: Notification):
        contest = admin_notification.contest
        contest_members = ContestPerson.objects.filter(
            contest=contest
        ).select_related('person')

        for contest_person in contest_members:
            tokens = cls.get_user_active_tokens(contest_person.person)
            if not tokens:
                continue

            payload = NotificationPayload(
                title=admin_notification.title,
                body=admin_notification.body,
                data={
                    'type': 'admin_notification',
                    'contest_id': str(contest.id),
                    'notification_id': str(admin_notification.id),
                }
            )

            result = FCMService.send_to_tokens(tokens, payload)
            cls.delete_invalid_tokens(result['invalid_tokens'])

            NotificationLog.objects.create(
                receiver=contest_person,
                notification_type='admin_notification',
                success=result['success'] > 0,
                error_message=f"Success: {result['success']}, Failed: {result['failure']}"
            )

        # Mark notification as sent
        admin_notification.is_sent = True
        admin_notification.sent_at = timezone.now()
        admin_notification.save()
