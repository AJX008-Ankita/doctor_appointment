import json
from datetime import date
from django.urls import reverse   
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User

from .forms import DoctorAvailabilityForm
from .models import Doctor, Appointment, DoctorAvailability, MedicalNote
from apps.accounts.models import Patient

# DRF
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@login_required
def doctor_dashboard(request):
    if not hasattr(request.user, "profile"):
        return redirect("doctor_login")

    if request.user.profile.role != "doctor":
        return redirect("doctor_login")   # block patient

    return render(request, "appointments/doctor_dashboard.html")


@login_required
def patient_dashboard(request):
    if not hasattr(request.user, "profile"):
        return redirect("patient_login")

    if request.user.profile.role != "patient":
        return redirect("patient_login")  # block doctor

    return render(request, "appointments/patient_dashboard.html")

# =from django.shortcuts import get_object_or_404

# =====================================================
# API: SEARCH DOCTORS BY PROBLEM (SWAGGER)
# =====================================================
from rest_framework.permissions import AllowAny, IsAuthenticated
@api_view(['GET'])
@permission_classes([AllowAny])
def api_search_doctors(request):
    name = request.GET.get("name", "").strip()
    city = request.GET.get("city", "").strip()
    specialization = request.GET.get("specialization", "").strip()

    doctors = Doctor.objects.all()

    if name:
        doctors = doctors.filter(full_name__icontains=name)
    if city:
        doctors = doctors.filter(city__icontains=city)
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)

    data = []
    for doc in doctors:
        data.append({
            "id": doc.id,
            "name": doc.full_name,
            "email": doc.user.email,
            "phone": doc.phone,
            "specialization": doc.specialization,
            "qualification": doc.qualification,
            "experience_years": doc.experience_years,
            "clinic_name": doc.clinic_name,
            "city": doc.city,
            "consultation_fee": doc.consultation_fee,
            "profile_image": doc.profile_image.url if doc.profile_image else None,
        })

    return Response(data, status=status.HTTP_200_OK)

# =====================================================
# API: CREATE APPOINTMENT (SWAGGER)
# =====================================================
@require_POST
def create_appointment_api(request):

    # 🔐 If not logged in → return message + login link
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "success": False,
                "error": "Please login to book an appointment",
                "login_url": reverse("patient_login")
            },
            status=401
        )

    data = json.loads(request.body)

    availability_id = data.get("availability_id")
    patient_start_time = data.get("patient_start_time")
    patient_end_time = data.get("patient_end_time")

    availability = get_object_or_404(
        DoctorAvailability,
        id=availability_id,
        is_available=True
    )

    patient = get_object_or_404(Patient, user=request.user)
    doctor = get_object_or_404(Doctor, user=availability.doctor)

    if Appointment.objects.filter(
        patient=patient,
        appointment_date=availability.date,
        patient_start_time=patient_start_time,
        patient_end_time=patient_end_time
    ).exists():
        return JsonResponse(
            {"success": False, "error": "You already booked this slot"},
            status=400
        )

    appointment = Appointment.objects.create(
        doctor=doctor,
        patient=patient,
        appointment_date=availability.date,
        start_time=availability.start_time,
        end_time=availability.end_time,
        patient_start_time=patient_start_time,
        patient_end_time=patient_end_time,
        status="scheduled"
    )

    return JsonResponse({
        "success": True,
        "appointment_id": appointment.id
    })
# =====================================================
# API: CHECK-IN APPOINTMENT (SWAGGER)
# =====================================================
@login_required
def patient_checkin_appointment(request, appointment_id):
    patient = get_object_or_404(Patient, user=request.user)

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=patient
    )

    if appointment.status == "scheduled":
        appointment.status = "checked_in"
        appointment.save()

    return redirect("patient_appointment_status")



# =====================================================
# API: CANCEL APPOINTMENT (SWAGGER)
# =====================================================
@login_required
def patient_cancel_appointment(request, appointment_id):
    patient = get_object_or_404(Patient, user=request.user)

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=patient
    )

    if appointment.status not in ["completed", "cancelled_by_patient"]:
        appointment.status = "cancelled_by_patient"
        appointment.save()

    return redirect("patient_appointment_status")

# ==============================
# HTML PAGE: DOCTOR SEARCH
# ==============================
# -----------------------------
# Doctor Search Page (PUBLIC)
# -----------------------------
def doctor_search_page(request):
    return render(request, "appointments/doctor_search.html")

# -----------------------------
# Book Appointment Page
# -----------------------------
def book_appointment_page(request, doctor_id):

    doctor = get_object_or_404(Doctor, id=doctor_id)

    availability_slots = DoctorAvailability.objects.filter(
        doctor=doctor.user,
        is_available=True,
        date__gte=date.today()
    ).order_by("date", "start_time")

    return render(
        request,
        "appointments/book_appointment.html",
        {
            "doctor": doctor,
            "availability_slots": availability_slots
        }
    )


# def doctor_search_page(request):
#     return render(request, "appointments/doctor_search.html")


    # ==============================
    # doctor who is being booked for is passed to the template, so that we can show doctor details and
    # also use doctor.id when creating appointment via API
# ==============================
@login_required
def doctor_today_appointments(request):
    if not hasattr(request.user, "profile") or request.user.profile.role != "doctor":
        return redirect("doctor_login")

    today = date.today()

    appointments = Appointment.objects.filter(
        doctor__user=request.user
    ).select_related("patient", "patient__user").order_by("-appointment_date", "start_time")

    return render(
        request,
        "appointments/doctor_today_appointments.html",
        {
            "appointments": appointments,
            "today": today
        }
    )
@login_required
def doctor_update_appointment(request, pk):
    # Doctor-only access
    if not hasattr(request.user, "profile") or request.user.profile.role != "doctor":
        return redirect("doctor_login")

    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        doctor__user=request.user
    )

    if request.method == "POST":
        appointment.status = request.POST.get("status")
        appointment.save()

    return redirect("doctor_today_appointments")

@login_required
def doctor_delete_appointment(request, pk):
    if not hasattr(request.user, "profile") or request.user.profile.role != "doctor":
        return redirect("doctor_login")

    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        doctor__user=request.user
    )

    appointment.delete()
    return redirect("doctor_today_appointments")

# ==============================
# patient_appointments_status
# =============================
@login_required
def patient_appointments_status(request):
    if not hasattr(request.user, "profile") or request.user.profile.role != "patient":
        return redirect("patient_login")

    patient = get_object_or_404(Patient, user=request.user)

    appointments = Appointment.objects.filter(
        patient=patient
    ).select_related("doctor", "doctor__user").order_by("-appointment_date")

    return render(
        request,
        "appointments/patient_appointment_status.html",
        {
            "appointments": appointments
        }
    )
# ==============================
# doctor availability management
# ==============================
@login_required
def doctor_set_availability(request):
    if request.method == "POST":
        form = DoctorAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.doctor = request.user
            availability.save()
            return redirect("doctor_availability_list")
    else:
        form = DoctorAvailabilityForm()

    return render(request, "appointments/doctor_set_availability.html", {
        "form": form
    })
    #=============================================================
    # doctor sets availability for a specific date and time range. This will be used to
    #============================================================


@login_required
def doctor_availability_list(request):
    slots = DoctorAvailability.objects.filter(doctor=request.user)
    return render(
        request,
        "appointments/doctor_availability_list.html",
        {"slots": slots}
    )


#=============================================================
#DELETE AVAILABILITY
#=============================================================
@login_required
def delete_availability(request, pk):
    slot = get_object_or_404(DoctorAvailability, pk=pk, doctor=request.user)
    slot.delete()
    return redirect("doctor_availability_list")

    #=============================================================
  

@login_required
def mark_present(request, id):
    appointment = get_object_or_404(Appointment, id=id)

    if request.method == "POST":
        appointment.status = "checked_in"
        appointment.save()

    return redirect("doctor_today_appointments")

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from reportlab.pdfgen import canvas
import os

from .models import Appointment, MedicalNote


# -------------------
# WRITE NOTES PAGE
# -------------------
def write_notes(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, "appointments/write_notes.html", {
        "appointment": appointment
    })


# -------------------
# SAVE NOTES (FETCH)
# -------------------
@csrf_exempt
def save_notes(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)

        MedicalNote.objects.update_or_create(
            appointment=appointment,
            defaults={
                "notes": request.POST.get("notes"),
                "prescription": request.POST.get("prescription"),
                "follow_up": request.POST.get("follow_up"),
            }
        )

        return JsonResponse({
            "status": "success",
            "message": "Notes saved successfully"
        })

    return JsonResponse({"error": "Invalid request"}, status=400)




# -------------------
# REPORT PREVIEW
# -------------------
def report_preview(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, "appointments/report_preview.html", {
        "appointment": appointment
    })


# -------------------
# GENERATE PDF (ReportLab)
# -------------------
def generate_report(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    try:
        note = MedicalNote.objects.get(appointment=appointment)
    except MedicalNote.DoesNotExist:
        return HttpResponse("Medical note not found")

    reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    file_path = os.path.join(reports_dir, f"appointment_{appointment.id}.pdf")

    c = canvas.Canvas(file_path)
    c.setFont("Helvetica", 12)

    y = 800
    c.drawString(50, y, "MEDICAL REPORT")
    y -= 40

    c.drawString(50, y, f"Patient: {appointment.patient.full_name}")
    y -= 20
    c.drawString(50, y, f"Doctor: {appointment.doctor.full_name}")
    y -= 20
    c.drawString(50, y, f"Date: {appointment.appointment_date}")
    y -= 40

    c.drawString(50, y, "Notes:")
    y -= 20
    c.drawString(70, y, note.notes)
    y -= 40

    c.drawString(50, y, "Prescription:")
    y -= 20
    c.drawString(70, y, note.prescription)
    y -= 40

    c.drawString(50, y, "Follow Up:")
    y -= 20
    c.drawString(70, y, note.follow_up)

    c.showPage()
    c.save()

    appointment.report_pdf.name = f"reports/appointment_{appointment.id}.pdf"
    appointment.save()

    return FileResponse(open(file_path, "rb"), content_type="application/pdf")
#==============================================================
#patient reschdule appointment
#=============================================================
@login_required
def patient_reschedule_appointment(request, appointment_id):
    patient = get_object_or_404(Patient, user=request.user)

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=patient
    )

    if request.method == "POST":
        appointment.appointment_date = request.POST.get("appointment_date")
        appointment.start_time = request.POST.get("start_time")
        appointment.end_time = request.POST.get("end_time")
        appointment.status = "scheduled"
        appointment.save()

        return redirect("patient_appointment_status")

    return render(
        request,
        "appointments/patient_reschedule.html",
        {"appointment": appointment}
    )

