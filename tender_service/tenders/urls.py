from django.urls import path

from .views import (
    MyTenderListAPIView, TenderCreateAPIView, TenderListAPIView, TenderRollbackAPIView, TenderStatusAPIView,
    TenderUpdateAPIView
)

urlpatterns = [
    path('', TenderListAPIView.as_view()),
    path('/new', TenderCreateAPIView.as_view()),
    path('/my', MyTenderListAPIView.as_view()),
    path('/<uuid:tender_id>/status', TenderStatusAPIView.as_view()),
    path('/<uuid:tender_id>/edit', TenderUpdateAPIView.as_view()),
    path('/<uuid:tender_id>/rollback/<int:version>', TenderRollbackAPIView.as_view()),
]
