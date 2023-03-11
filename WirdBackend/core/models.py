import os
import uuid

from django.contrib.auth.models import User, AbstractUser
from django.core.validators import integer_validator
from django.db import models

from WirdBackend import settings


def upload_location(instance, filename):
    filebase, extension = filename.split('.')
    filename = f'{instance.competition.id}/{instance.username}.{extension}'
    if os.path.exists(settings.MEDIA_URL + filename):
        os.remove(settings.MEDIA_URL + filename)
    return filename


class Competition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, default='')
    show_standings = models.BooleanField(default=True)
    announcements = models.TextField(default="", blank=True)
    readonly_mode = models.BooleanField(default=False, help_text='Stop scoring points and only show scored points')
    access_code = id[-6:]

    def __str__(self):
        return self.name


class Person(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_photo = models.ImageField(upload_to=upload_location, blank=True)
    phone_number = models.CharField(max_length=15, validators=[integer_validator], default="0000000000", blank=True)


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30, default='')
    announcements = models.TextField(default="", blank=True)

    def __str__(self):
        return self.name


class CompPerson(models.Model):
    STATUS = (
        (1, 'default'),
        (2, 'admin'),
        (3, 'super_admin'),
        (4, 'pending_acceptance'),
        (5, 'pending_admin'),
        (6, 'deactivated'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comp = models.ForeignKey(Competition, on_delete=models.SET_NULL)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL)
    roles = models.PositiveSmallIntegerField(choices=STATUS, default=1)
