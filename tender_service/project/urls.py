from django.contrib import admin
from django.urls import include, path

API_PREFIX = 'api/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(API_PREFIX, include('tender_service.project.api_urls')),
]
