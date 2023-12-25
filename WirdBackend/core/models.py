import uuid
from gettext import gettext

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres import fields
from django.core.validators import integer_validator, MinLengthValidator
from django.db import models
from django_resized import ResizedImageField


def upload_location(instance, filename):
    extension = filename.split('.')[-1]
    if instance is Person:
        filename = f'{instance.username}_profile_photo.{extension}'
    elif instance is Contest:
        filename = f'{instance.id}_contest_photo.{extension}'
    return filename


class Contest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contest_id = models.CharField(unique=True, max_length=12, default="", validators=[MinLengthValidator(6)])
    name = models.CharField(max_length=128, validators=[MinLengthValidator(4)], default='')
    description = models.CharField(max_length=500, blank=True)
    show_standings = models.BooleanField(default=True)
    announcements = fields.ArrayField(models.CharField(max_length=500), blank=True, default=[])
    readonly_mode = models.BooleanField(default=False, help_text=gettext('readonly_mode'))
    contest_photo = ResizedImageField(size=[500, 500], upload_to=upload_location, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class Person(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_photo = ResizedImageField(size=[500, 500], upload_to=upload_location, blank=True)
    phone_number = models.CharField(max_length=15, validators=[integer_validator], default="0000000000", blank=True)


class ContestPerson(models.Model):
    class ContestRole(models.IntegerChoices):
        CONTEST_OWNER = (0, 'contest_owner')
        SUPER_ADMIN = (1, 'super_admin')
        ADMIN = (2, 'admin')
        MEMBER = (3, 'member')
        READ_ONLY_MEMBER = (4, 'read_only_member')
        PENDING_MEMBER = (5, 'pending_member')
        DEACTIVATED = (6, 'deactivated')

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    contest_role = models.PositiveSmallIntegerField(choices=ContestRole.choices, default=ContestRole.MEMBER)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['contest_id', 'person_id'],
                                    name="unique_contest_person",
                                    violation_error_message=gettext("person exists in contest")),
        ]

    def __str__(self):
        return f"{self.person.username} @ {self.contest.name}"
