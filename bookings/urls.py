from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('conflicts/',
         views.BookingViewSet.as_view({'get': 'conflicts'}), name='booking-conflicts'),
]
