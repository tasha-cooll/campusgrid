from django.urls import path
from .views import (
    FacilityListView,
    FacilityCreateView,
    FacilityDetailView,
    FacilityHoursView,
)

app_name = 'facilities'

urlpatterns = [
    path('',              FacilityListView.as_view(),   name='facility-list'),
    path('create/',       FacilityCreateView.as_view(), name='facility-create'),
    path('<int:pk>/',     FacilityDetailView.as_view(), name='facility-detail'),
    path('<int:pk>/hours/', FacilityHoursView.as_view(), name='facility-hours'),
]
