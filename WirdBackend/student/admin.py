from django.contrib import admin

# Register your models here.
from student.models import StudentUser, PointRecord

admin.site.register(StudentUser)
admin.site.register(PointRecord)
