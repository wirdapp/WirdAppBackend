from django.contrib.auth.models import User
from django.db import models

from compAdmin.models import PointTemplate, CompGroup
from superAdmin.models import Competition


class StudentUser(User):
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True)
    total_points = models.FloatField(default=0.0)
    read_only = models.BooleanField(default=False)
    group = models.ForeignKey(CompGroup, on_delete=models.SET_NULL, null=True)


class PointRecord(models.Model):
    user = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    type = models.ForeignKey(PointTemplate, on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    details = models.CharField(max_length=256, default='')
    ramadan_record_date = models.IntegerField()
