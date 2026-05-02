from django.urls import path
from .views import (
    BookingListCreateView,
    BookingDetailView,
    ConflictCheckView,
)

app_name = 'bookings'

urlpatterns = [
    path('',                BookingListCreateView.as_view(),
         name='booking-list-create'),
    path('<int:pk>/',       BookingDetailView.as_view(),     name='booking-detail'),
    path('check-conflict/', ConflictCheckView.as_view(),     name='conflict-check'),
]
