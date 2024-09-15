from django.urls import include, path

from tender_service.core.views import PingView

urlpatterns = [
    path('ping', PingView.as_view()),
    path('tenders', include('tender_service.tenders.urls')),
    path('bids', include('tender_service.bids.urls')),
]
