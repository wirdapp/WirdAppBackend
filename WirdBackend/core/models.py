import uuid
from gettext import gettext

from django.contrib.auth.models import AbstractUser
from django.core.validators import integer_validator, MinLengthValidator
from django.db import models
from django.utils.functional import cached_property
from django_resized import ResizedImageField


class Contest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, validators=[MinLengthValidator(4)], default='')
    description = models.TextField(default='')
    show_standings = models.BooleanField(default=True)
    announcements = models.TextField(default="", blank=True)
    readonly_mode = models.BooleanField(default=False, help_text=gettext('readonly_mode'))

    @cached_property
    def access_code(self):
        return self.id.hex.upper()[-6:]

    @cached_property
    def admin_count(self):
        return ContestPerson.objects.filter(contest__id=self.id, contest_role__in=[2, 3]).count()

    @cached_property
    def member_count(self):
        return ContestPerson.objects.filter(contest__id=self.id, contest_role=1).count()

    @cached_property
    def group_count(self):
        return Group.objects.filter(contest__id=self.id).count()


def upload_location(instance, filename):
    extension = filename.split('.')[-1]
    filename = f'{instance.username}_profile_photo.{extension}'
    return filename


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
        MEMBER = (1, 'member')
        ADMIN = (2, 'admin')
        SUPER_ADMIN = (3, 'super_admin')
        DEACTIVATED = (4, 'deactivated')

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
