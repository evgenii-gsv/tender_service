from django.contrib import admin

from .models import Employee, Organization, OrganizationResponsible

admin.site.register(Employee)
admin.site.register(Organization)
admin.site.register(OrganizationResponsible)
