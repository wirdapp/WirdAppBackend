from random import randint

from django.contrib.auth.models import User, Permission
from django.db import models


class Competition(models.Model):
    id = models.CharField(max_length=30, primary_key=True, default='')
    code = models.IntegerField(blank=False, default=randint(1000, 9999))
    name = models.CharField(max_length=30, default='')
    show_standings = models.BooleanField(default=True)
    readonly_mode = models.BooleanField(default=False, help_text='Stop scoring points and only show scored points')

    def __str__(self):
        return self.name


class PointFormat(models.Model):
    id = models.CharField(max_length=64, default="", primary_key=True)
    label = models.CharField(max_length=64, default="")
    html = models.TextField(default="")
