from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from admin_panel.models import PointTemplate
from core.models import Person


class PointRecord(models.Model):
    point_template = models.ForeignKey(PointTemplate, on_delete=models.PROTECT)
    person = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='student_points')
    point_scored_units = models.IntegerField(default=0)
    ramadan_record_date = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    user_input = models.TextField(default="", blank=True, max_length=512)
    point_total = models.IntegerField(default=0)

    def set_student(self, student):
        self.student = student

    def set_point_total(self, point_total):
        self.point_total = point_total

    class Meta:
        ordering = ('-ramadan_record_date',)

    def __str__(self):
        return f'{self.student.username}:{self.point_template.label}:date:{self.ramadan_record_date}'
