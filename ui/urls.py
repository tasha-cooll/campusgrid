from django.urls import path
from . import views

app_name = 'ui'

urlpatterns = [
    path('',               views.login_view,        name='login'),
    path('signup/',        views.signup_view,        name='signup'),
    path('logout/',        views.logout_view,        name='logout'),
    path('calendar/',      views.calendar_view,      name='calendar'),
    path('dashboard/',     views.dashboard_view,     name='dashboard'),
    path('bookings/',      views.bookings_view,      name='bookings'),
    path('bookings/new/',  views.new_booking_view,   name='new-booking'),
    path('approvals/',     views.approvals_view,     name='approvals'),
    path('facilities/',    views.facilities_view,    name='facilities'),
    path('reports/',       views.reports_view,       name='reports'),
    path('notifications/', views.notifications_view, name='notifications'),
]
