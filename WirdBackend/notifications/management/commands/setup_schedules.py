from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = 'Setup Django-Q schedules for notifications'

    def handle(self, *args, **options):
        Schedule.objects.update_or_create(
            name='send_daily_reminders',
            defaults={
                'func': 'notifications.tasks.send_daily_reminders',
                'schedule_type': Schedule.HOURLY,
                'repeats': -1,  # Repeat forever
            }
        )
        self.stdout.write(
            self.style.SUCCESS('Successfully created notification schedules')
        )
