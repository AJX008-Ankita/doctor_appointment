from django.urls import path
from . import views

urlpatterns = [
    # LOGIN
   path("doctor/login/", views.doctor_login, name="doctor_login"),


 path("patient/login/", views.patient_login, name="patient_login"),


    # REGISTER PAGES
    path('doctor/register/', views.doctor_register, name='doctor_register'),
    path('patient/register/', views.patient_register, name='patient_register'),

    # REGISTER APIs
    path('api/doctor/register/', views.doctor_register_api, name='doctor_register_api'),
    path('api/patient/register/', views.patient_register_api, name='patient_register_api'),

    # LOGOUT API
    # apps/accounts/urls.py
# apps/accounts/urls.py
path("logout/", views.logout_view, name="logout"),
 

]
