from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from apps.appointments.views import patient_dashboard
from apps.appointments.views import patient_dashboard, doctor_dashboard

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.views import LogoutView

def home(request):
    return render(request, 'home.html')


schema_view = get_schema_view(
    openapi.Info(
        title="Appointment API",
        default_version='v1',
        description="All Appointment APIs",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),

    # APPS
    path('', include('apps.accounts.urls')),
 
    # ✅ THIS FIXES THE PROBLEM
    path("patient/dashboard/", patient_dashboard, name="patient_dashboard"),
      path("appointments/", include("apps.appointments.urls")),
     path("doctor/dashboard/", doctor_dashboard, name="doctor_dashboard"),


    # API DOCS
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    

]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
