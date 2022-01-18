from django.contrib import admin

# Register your models here.
from compAdmin.models import CompAdmin, Section, CompGroup, PointTemplate

admin.site.register(CompAdmin)
admin.site.register(Section)
admin.site.register(CompGroup)
admin.site.register(PointTemplate)
