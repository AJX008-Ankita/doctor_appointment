from django.urls import path
from . import views
from . import views as appointment_views


urlpatterns = [

    # =====================================================
    # DASHBOARDS (HTML)
    # =====================================================
  path("patient/dashboard/", appointment_views.patient_dashboard, name="patient_dashboard"),


    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),

    # =====================================================
    # PUBLIC DOCTOR SEARCH (HTML)
    # =====================================================
     path("doctor/search/", views.doctor_search_page, name="doctor_search_page"),
    # =====================================================
    # PUBLIC DOCTOR SEARCH (API)
    # =====================================================
#   # =============================
#     # DOCTOR SEARCH (HTML)
#     # =============================
#     path(
#         "doctor/search/",
#         views.doctor_search_page,
#         name="doctor_search_page"
#     ),

    # =============================
    # DOCTOR SEARCH (API)
    # =============================
    # =============================
    # DOCTOR SEARCH (API) ✅ ADD THIS
    # =============================
    path(
        "api/doctors/search/",
        views.api_search_doctors,
        name="api_search_doctors"
    ),

 # =============================
    # BOOK APPOINTMENT
    # =============================
    path(
        "book/<int:doctor_id>/",
        views.book_appointment_page,
        name="book_appointment_page"
    ),

    # =====================================================
    # PATIENT APPOINTMENTS (HTML)
    # =====================================================
    path(
        "patient/appointments/",
        views.patient_appointments_status,
        name="patient_appointment_status"
    ),
    path(
        "patient/appointment/<int:appointment_id>/checkin/",
        views.patient_checkin_appointment,
        name="patient_checkin_appointment"
    ),
    path(
        "patient/appointment/<int:appointment_id>/cancel/",
        views.patient_cancel_appointment,
        name="patient_cancel_appointment"
    ),
    path(
        "patient/appointment/<int:appointment_id>/reschedule/",
        views.patient_reschedule_appointment,
        name="patient_reschedule_appointment"
    ),

    # =====================================================
    # DOCTOR APPOINTMENTS (HTML)
    # =====================================================
    path(
        "doctor/today/",
        views.doctor_today_appointments,
        name="doctor_today_appointments"
    ),
    path(
        "doctor/appointment/<int:pk>/update/",
        views.doctor_update_appointment,
        name="doctor_update_appointment"
    ),
    path(
        "doctor/appointment/<int:pk>/delete/",
        views.doctor_delete_appointment,
        name="doctor_delete_appointment"
    ),
    path(
        "appointment/<int:id>/mark-present/",
        views.mark_present,
        name="mark_present"
    ),

    # =====================================================
    # MEDICAL NOTES & REPORTS
    # =====================================================
    path(
        "appointment/<int:appointment_id>/write-notes/",
        views.write_notes,
        name="write_notes"
    ),
    path(
        "appointment/<int:appointment_id>/save-notes/",
        views.save_notes,
        name="save_notes"
    ),
path(
    "appointment/<int:appointment_id>/report/",
    views.generate_report,
    name="report_preview"
),

   path("report/<int:appointment_id>/", views.generate_report, name="generate_report"),

    # =====================================================
    # DOCTOR AVAILABILITY
    # =====================================================
    path(
        "doctor/availability/",
        views.doctor_availability_list,
        name="doctor_availability_list"
    ),
    path(
        "doctor/availability/add/",
        views.doctor_set_availability,
        name="doctor_set_availability"
    ),
    path(
        "doctor/availability/delete/<int:pk>/",
        views.delete_availability,
        name="delete_availability"
    ),

    # =====================================================
    # APPOINTMENT API (LOGIN REQUIRED)
    # =====================================================
    path(
        "api/appointments/create/",
        views.create_appointment_api,
        name="create_appointment_api"
    ),
]
