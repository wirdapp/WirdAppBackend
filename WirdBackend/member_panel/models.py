import datetime
import uuid

from django.db import models
from polymorphic.models import PolymorphicModel

from admin_panel.models import PointTemplate
from core.models import ContestPerson


class PointRecord(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(ContestPerson, on_delete=models.PROTECT, related_name='contest_person_points')
    point_template = models.ForeignKey(PointTemplate, on_delete=models.PROTECT)
    record_date = models.DateField(default=datetime.date.today)
    units_scored = models.PositiveIntegerField(
        help_text="Number in case of Number Template, "
                  "0 and 1 for the Boolean Template, "
                  "0 (empty) and 1 (filled) for other templates"
        , default=0
    )
    point_total = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-record_date',)

    def __str__(self):
        return f'{self.person.person_id}:{self.point_template.label}:date:{self.record_date}'

    @property
    def record_type(self):
        return self.__class__.__name__


class UserInputPointRecord(PointRecord):
    user_input = models.TextField(default="", blank=True, max_length=1024)
    reviewed_by_admin = models.BooleanField(default=False)
