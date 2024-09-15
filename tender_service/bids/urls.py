from django.urls import path

from .views import (
    BidCreateAPIView, BidFeedbackAPIView, BidFeedbackListAPIView, BidRollbackAPIView, BidStatusAPIView,
    BidUpdateAPIView, MyBidListAPIView, SubmitDecisionAPIView, TenderBidListAPIView
)

urlpatterns = [
    path('/new', BidCreateAPIView.as_view()),
    path('/my', MyBidListAPIView.as_view()),
    path('/<uuid:tender_id>/list', TenderBidListAPIView.as_view()),
    path('/<uuid:bid_id>/status', BidStatusAPIView.as_view()),
    path('/<uuid:bid_id>/edit', BidUpdateAPIView.as_view()),
    path('/<uuid:bid_id>/rollback/<int:version>', BidRollbackAPIView.as_view()),
    path('/<uuid:bid_id>/feedback', BidFeedbackAPIView.as_view()),
    path('/<uuid:tender_id>/reviews', BidFeedbackListAPIView.as_view()),
    path('/<uuid:bid_id>/submit_decision', SubmitDecisionAPIView.as_view()),
]
