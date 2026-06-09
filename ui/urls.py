from django.urls import path
from . import views

app_name = 'ui'

urlpatterns = [
    path('',                  views.login_view,              name='login'),
    path('signup/',           views.signup_view,             name='signup'),
    path('logout/',           views.logout_view,             name='logout'),
    path('change-password/',  views.change_password_view,    name='change-password'),
    path('calendar/',         views.calendar_view,           name='calendar'),
    path('dashboard/',        views.dashboard_view,          name='dashboard'),
    path('bookings/',         views.bookings_view,           name='bookings'),
    path('bookings/new/',     views.new_booking_view,        name='new-booking'),
    path('bookings/confirm/', views.booking_confirmation_view,
         name='booking-confirm'),
    path('approvals/',        views.approvals_view,          name='approvals'),
    path('facilities/',       views.facilities_view,         name='facilities'),
    path('reports/',          views.reports_view,            name='reports'),
    path('notifications/',    views.notifications_view,      name='notifications'),
    path('users/',            views.users_view,              name='users'),
    path('audit-log/', views.audit_log_view, name='audit-log'),
]
