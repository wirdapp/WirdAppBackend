import datetime
import uuid

from django.db import models
from django.db.models import Q
from polymorphic.models import PolymorphicModel

from admin_panel.models import PointTemplate
from core.models import ContestPerson


class PointRecord(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(ContestPerson, on_delete=models.PROTECT, related_name='contest_person_points')
    point_template = models.ForeignKey(PointTemplate, on_delete=models.PROTECT)
    record_date = models.DateField(default=datetime.date.today)
    point_total = models.IntegerField(default=0)

    class Meta:
        ordering = ('-record_date',)
        constraints = [
            models.CheckConstraint(check=Q(person__contest_role=1), name="members_only_check",
                                   violation_error_message="Only Members can score points")
        ]

    def __str__(self):
        return f'{self.person.person_id}:{self.point_template.label}:date:{self.record_date}'


class UserInputPointRecord(PointRecord):
    user_input = models.TextField(default="", blank=True, max_length=1024)
    reviewed_by_admin = models.BooleanField(default=False)
