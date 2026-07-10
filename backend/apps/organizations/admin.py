from django.contrib import admin
from .models import Organization, Branch, Department, Team


admin.site.register(Organization)
admin.site.register(Branch)
admin.site.register(Department)
admin.site.register(Team)