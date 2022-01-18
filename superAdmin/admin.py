from django.contrib import admin

# Register your models here.
from superAdmin.models import Competition, PointFormat

admin.site.register(Competition)
admin.site.register(PointFormat)
