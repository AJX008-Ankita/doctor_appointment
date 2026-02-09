from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from apps.appointments.views import patient_dashboard, doctor_dashboard

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def home(request):
    return render(request, 'home.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),

    # APPS
    path('', include('apps.accounts.urls')),
    path("appointments/", include("apps.appointments.urls")),

    # DASHBOARDS
    path("patient/dashboard/", patient_dashboard, name="patient_dashboard"),
    path("doctor/dashboard/", doctor_dashboard, name="doctor_dashboard"),

    # API DOCUMENTATION (Python 3.13 compatible)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema')),

    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
