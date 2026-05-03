from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationReadView,
    MarkAllReadView,
    UnreadCountView,
)

app_name = 'notifications'

urlpatterns = [
    path('',                        NotificationListView.as_view(),     name='list'),
    path('<int:pk>/read/',
         MarkNotificationReadView.as_view(), name='mark-read'),
    path('mark-all-read/',          MarkAllReadView.as_view(),
         name='mark-all-read'),
    path('unread-count/',           UnreadCountView.as_view(),
         name='unread-count'),
]
