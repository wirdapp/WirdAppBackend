from django.contrib import admin

from admin_panel.models import *

admin.site.register(Section)
admin.site.register(CheckboxCriterion)
admin.site.register(NumberCriterion)
admin.site.register(RadioCriterion)
admin.site.register(MultiCheckboxCriterion)

