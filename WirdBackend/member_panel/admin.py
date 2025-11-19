from django.contrib import admin

from member_panel.models import *

admin.site.register(NumberPointRecord)
admin.site.register(CheckboxPointRecord)
admin.site.register(UserInputPointRecord)
admin.site.register(RadioPointRecord)
admin.site.register(MultiCheckboxPointRecord)
