from django.contrib import admin

# Register your models here.
from compAdmin.models import *

admin.site.register(CompAdmin)
admin.site.register(Section)
admin.site.register(CompGroup)
admin.site.register(PointTemplate)
admin.site.register(Competition)
admin.site.register(PointFormat)
