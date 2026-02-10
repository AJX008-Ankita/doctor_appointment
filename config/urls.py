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


# =========================
# HOME VIEW
# =========================
def home(request):
    return render(request, "home.html")


# =========================
# URL PATTERNS
# =========================
urlpatterns = [
    # ADMIN
    path("admin/", admin.site.urls),

    # HOME
    path("", home, name="home"),

    # APPS (IMPORTANT: prefixed, no conflicts)
    path("accounts/", include("apps.accounts.urls")),
    path("appointments/", include("apps.appointments.urls")),

    # DASHBOARDS
    path("patient/dashboard/", patient_dashboard, name="patient_dashboard"),
    path("doctor/dashboard/", doctor_dashboard, name="doctor_dashboard"),

    # AUTH
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),

    # API DOCUMENTATION
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# =========================
# MEDIA FILES (DEV ONLY)
# =========================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
