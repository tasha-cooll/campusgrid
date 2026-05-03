from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Auth
    path('api/auth/login/',   TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # App routers
    path('api/auth/',          include('accounts.urls')),
    path('api/facilities/',    include('facilities.urls')),
    path('api/bookings/',      include('bookings.urls')),
    path('api/approvals/',     include('approvals.urls')),
    path('api/reports/',       include('reports.urls')),
    path('api/notifications/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
