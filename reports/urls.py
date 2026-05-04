from django.urls import path
from .views import (
    CalendarView,
    UtilizationReportView,
    ConflictReportView,
    DashboardSummaryView,
    AuditLogView,
)

app_name = 'reports'

urlpatterns = [
    path('calendar/',     CalendarView.as_view(),         name='calendar'),
    path('utilization/',  UtilizationReportView.as_view(), name='utilization'),
    path('conflicts/',    ConflictReportView.as_view(),    name='conflicts'),
    path('dashboard/',    DashboardSummaryView.as_view(),  name='dashboard'),
    path('audit-log/',    AuditLogView.as_view(),          name='audit-log'),
]
