import uuid
from gettext import gettext

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres import fields
from django.core.validators import integer_validator, MinLengthValidator
from django.db import models
from django.utils.functional import cached_property
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

    @cached_property
    def admin_count(self):
        return ContestPerson.objects.filter(contest__id=self.id, contest_role__in=[1, 2]).count()

    @cached_property
    def member_count(self):
        return ContestPerson.objects.filter(contest__id=self.id, contest_role=3).count()

    @cached_property
    def group_count(self):
        return Group.objects.filter(contest__id=self.id).count()


class Person(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_photo = ResizedImageField(size=[500, 500], upload_to=upload_location, blank=True)
    phone_number = models.CharField(max_length=15, validators=[integer_validator], default="0000000000", blank=True)


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    announcements = models.TextField(default="", blank=True)
    contest = models.ForeignKey("core.Contest", on_delete=models.PROTECT)

    @cached_property
    def members_count(self):
        return ContestPersonGroups.objects.filter(group_role=1, group__id=self.id).count()

    @cached_property
    def admins_count(self):
        return ContestPersonGroups.objects.filter(group_role=2, group__id=self.id).count()

    def __str__(self):
        return self.name


class ContestPerson(models.Model):
    class ContestRole(models.IntegerChoices):
        CONTEST_OWNER = (0, 'contest_owner')
        SUPER_ADMIN = (1, 'super_admin')
        ADMIN = (2, 'admin')
        MEMBER = (3, 'member')
        READ_ONLY_MEMBER = (4, 'read_only_member')
        PENDING_MEMBER = (5, 'pending_member')
        DEACTIVATED = (6, 'deactivated')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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


class ContestPersonGroups(models.Model):
    class GroupRole(models.IntegerChoices):
        MEMBER = (1, 'member')
        ADMIN = (2, 'admin')

    contest_person = models.ForeignKey(ContestPerson, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    group_role = models.PositiveSmallIntegerField(choices=GroupRole.choices, default=GroupRole.MEMBER)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['contest_person_id', 'group_id'],
                                    name="unique_group_person",
                                    violation_error_message=gettext("person is member of group")),
        ]
