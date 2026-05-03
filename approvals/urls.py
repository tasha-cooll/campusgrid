from django.urls import path
from .views import (
    PendingBookingsView,
    ApproveBookingView,
    RejectBookingView,
    ApprovalHistoryView,
)

app_name = 'approvals'

urlpatterns = [
    path('pending/',
         PendingBookingsView.as_view(),  name='pending'),
    path('<int:booking_id>/approve/',
         ApproveBookingView.as_view(),   name='approve'),
    path('<int:booking_id>/reject/',
         RejectBookingView.as_view(),    name='reject'),
    path('history/',
         ApprovalHistoryView.as_view(),  name='history'),
]
