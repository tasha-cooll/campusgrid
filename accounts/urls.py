from django.urls import path
from .views import RegisterView, MeView, UserListView, ChangeRoleView

app_name = 'accounts'

urlpatterns = [
    path('register/',           RegisterView.as_view(),   name='register'),
    path('me/',                 MeView.as_view(),          name='me'),
    path('users/',              UserListView.as_view(),    name='user-list'),
    path('users/<int:pk>/role/', ChangeRoleView.as_view(), name='change-role'),
]
