import uuid

from django.contrib.auth.models import User, AbstractUser
from django.core.validators import integer_validator
from django.db import models
from django_resized import ResizedImageField


class Contest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, default='')
    show_standings = models.BooleanField(default=True)
    announcements = models.TextField(default="", blank=True)
    readonly_mode = models.BooleanField(default=False, help_text='Stop scoring points and only show scored points')

    @property
    def access_code(self):
        return self.id.hex.upper()[-6:]


def upload_location(instance, filename):
    extension = filename.split('.')[-1]
    filename = f'{instance.username}_profile_photo.{extension}'
    return filename


class Person(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_photo = ResizedImageField(size=[500, 500], upload_to=upload_location, blank=True)
    phone_number = models.CharField(max_length=15, validators=[integer_validator], default="0000000000", blank=True)


class ContestPerson(models.Model):
    CONTEST_ROLE = (
        (1, 'member'),
        (2, 'admin'),
        (3, 'super_admin'),
        (4, 'pending_member'),
        (5, 'deactivated'),
    )
    GROUP_ROLE = (
        (1, 'member'),
        (2, 'admin'),
    )
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT, blank=True, null=True)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    group = models.ForeignKey("admin_panel.Group", on_delete=models.PROTECT, blank=True, null=True)
    contest_role = models.PositiveSmallIntegerField(choices=CONTEST_ROLE, default=1)
    group_role = models.PositiveSmallIntegerField(choices=GROUP_ROLE, default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['contest_id', 'person_id', 'contest_role'],
                                    name="unique_contest_person"),
            models.UniqueConstraint(fields=['contest_id', 'person_id', 'group_id', 'group_role'],
                                    name="unique_group_person")
        ]
