
from io import BytesIO
from reportlab.lib.pagesizes import A4
import cloudinary
import cloudinary.uploader
from django.http import HttpResponse, FileResponse
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
# views.py
#==============================================================

# ---------- helper functions ----------

def draw_kv(c, x, y, label, value):
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, f"{label}:")
    c.setFont("Helvetica", 11)
    c.drawString(x + 120, y, str(value))


def draw_section_title(c, x, y, title):
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, title)


# ---------- main function ----------

def generate_report(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    try:
        note = appointment.medical_note
    except MedicalNote.DoesNotExist:
        return HttpResponse("Medical note not found", status=404)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    line_gap = 18

    # =====================
    # HEADER
    # =====================
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, y, "MEDICAL REPORT")
    y -= 40

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Appointment ID: {appointment.id}")
    y -= line_gap
    c.drawString(
        50,
        y,
        f"Date: {appointment.appointment_date.strftime('%d %b %Y')}"
    )
    y -= line_gap
    c.drawString(
        50,
        y,
        f"Time: {appointment.start_time.strftime('%I:%M %p')} "
        f"to {appointment.end_time.strftime('%I:%M %p')}"
    )

    y -= 35

    # =====================
    # DOCTOR DETAILS (LEFT COLUMN)
    # =====================
    doctor = appointment.doctor
    left_x = 50
    right_x = 330

    draw_section_title(c, left_x, y, "Doctor Details")
    y_doctor = y - 25

    draw_kv(c, left_x, y_doctor, "Name", f"Dr. {doctor.full_name}"); y_doctor -= line_gap
    draw_kv(c, left_x, y_doctor, "Specialization", doctor.specialization); y_doctor -= line_gap
    draw_kv(c, left_x, y_doctor, "Qualification", doctor.qualification); y_doctor -= line_gap
    draw_kv(c, left_x, y_doctor, "Experience", f"{doctor.experience_years} years"); y_doctor -= line_gap
    draw_kv(c, left_x, y_doctor, "Clinic", doctor.clinic_name); y_doctor -= line_gap
    draw_kv(c, left_x, y_doctor, "City", doctor.city); y_doctor -= line_gap
    draw_kv(c, left_x, y_doctor, "Contact", doctor.phone)

    # =====================
    # PATIENT DETAILS (RIGHT COLUMN)
    # =====================
    patient = appointment.patient
    draw_section_title(c, right_x, y, "Patient Details")
    y_patient = y - 25

    draw_kv(c, right_x, y_patient, "Name", patient.full_name); y_patient -= line_gap
    draw_kv(c, right_x, y_patient, "Gender", patient.gender); y_patient -= line_gap
    draw_kv(c, right_x, y_patient, "Age", f"{patient.age} years"); y_patient -= line_gap
    draw_kv(c, right_x, y_patient, "City", patient.city); y_patient -= line_gap
    draw_kv(c, right_x, y_patient, "Contact", patient.phone)

    # Move y below both columns
    y = min(y_doctor, y_patient) - 30

    # =====================
    # MEDICAL NOTES
    # =====================
    draw_section_title(c, 50, y, "Medical Notes")
    y -= 22
    c.setFont("Helvetica", 11)
    y = draw_paragraph(c, note.notes, 70, y, max_width=460)
    y -= 25

    # =====================
    # PRESCRIPTION
    # =====================
    draw_section_title(c, 50, y, "Prescription")
    y -= 22
    y = draw_paragraph(c, note.prescription, 70, y, max_width=460)
    y -= 25

    # =====================
    # FOLLOW UP
    # =====================
    draw_section_title(c, 50, y, "Follow Up")
    y -= 22
    y = draw_paragraph(c, note.follow_up, 70, y, max_width=460)

    # =====================
    # FOOTER
    # =====================
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 40, "Generated by DocApp – Digital Medical Record")

    c.showPage()
    c.save()
    buffer.seek(0)

    if request.GET.get("download"):
        response = FileResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="medical_report_{appointment.id}.pdf"'
        )
        return response

    return FileResponse(buffer, content_type="application/pdf")


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

from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import black

def draw_paragraph(canvas, text, x, y, max_width):
    """
    Draw wrapped text without black boxes
    """
    if not text:
        return y

    style = ParagraphStyle(
        name="Normal",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=black,
        alignment=TA_LEFT,
    )

    para = Paragraph(text.replace("\n", "<br/>"), style)
    width, height = para.wrap(max_width, 1000)
    para.drawOn(canvas, x, y - height)
    return y - height - 10
