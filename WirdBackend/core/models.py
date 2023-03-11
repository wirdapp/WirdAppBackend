import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import integer_validator, MinLengthValidator
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django_resized import ResizedImageField


class Contest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, validators=[MinLengthValidator(4)], default='')
    description = models.TextField(default='')
    show_standings = models.BooleanField(default=True)
    announcements = models.TextField(default="", blank=True)
    readonly_mode = models.BooleanField(default=False, help_text='Stop scoring points and only show scored points')

    @cached_property
    def access_code(self):
        return self.id.hex.upper()[-6:]

    @cached_property
    def admin_count(self):
        return ContestPerson.objects.filter(contest__id=self.id, contest_role__in=[2, 3]).values_list("person__id") \
            .distinct().count()

    @cached_property
    def member_count(self):
        return ContestPerson.objects.filter(contest__id=self.id, contest_role=1).values_list("person__id") \
            .distinct().count()

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
        return ContestPerson.objects.filter(contest_role=1, group__id=self.id).count()

    def __str__(self):
        return self.name


class ContestPerson(models.Model):
    class ContestRole(models.IntegerChoices):
        MEMBER = (1, 'member')
        ADMIN = (2, 'admin')
        SUPER_ADMIN = (3, 'super_admin')
        PENDING_MEMBER = (4, 'pending_member')
        DEACTIVATED = (5, 'deactivated')

    contest = models.ForeignKey(Contest, on_delete=models.PROTECT, blank=True, null=True)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, blank=True, null=True)
    contest_role = models.PositiveSmallIntegerField(choices=ContestRole.choices, default=ContestRole.MEMBER)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['contest_id', 'person_id'],
                                    name="unique_group_person",
                                    violation_error_message="Can't Create more than one person in a contest"),
            models.CheckConstraint(check=~Q(contest_role=3) | Q(group=None),
                                   name="Super Admin can't be assigned to a group")
        ]
