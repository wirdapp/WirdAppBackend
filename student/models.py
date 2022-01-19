from django.db import models

from compAdmin.models import PointTemplate, CompGroup
from core.models import GeneralUser
from superAdmin.models import Competition


class StudentUser(GeneralUser):
    total_points = models.FloatField(default=0.0)
    read_only = models.BooleanField(default=False)
    group = models.ForeignKey(CompGroup, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ('first_name', 'last_name',)


class PointRecord(models.Model):
    user = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    type = models.ForeignKey(PointTemplate, on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    details = models.CharField(max_length=256, default='')
    ramadan_record_date = models.IntegerField()

    class Meta:
        ordering = ('-ramadan_record_date',)
