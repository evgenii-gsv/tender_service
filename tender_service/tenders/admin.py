from django.contrib import admin

from .models import Tender, TenderVersion

admin.site.register(Tender)
admin.site.register(TenderVersion)
