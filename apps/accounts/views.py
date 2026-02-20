import json
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .models import Doctor, Patient, Profile
from .serializers import (
    DoctorRegisterSerializer,
    DoctorLoginSerializer,
    PatientRegisterSerializer,
    PatientLoginSerializer,
)

# =====================================================
# PATIENT REGISTER PAGE (HTML)
# =====================================================
def patient_register(request):
    return render(request, "accounts/patient_register.html")


# =====================================================
# DOCTOR REGISTER PAGE (HTML)
# =====================================================
def doctor_register(request):
    return render(request, "accounts/doctor_register.html")


# =====================================================
# DOCTOR REGISTER API
# =====================================================
@extend_schema(
    request=DoctorRegisterSerializer,
    responses={201: dict},
)
@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def doctor_register_api(request):
    serializer = DoctorRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    full_name = data["full_name"].strip()
    email = data["email"].strip().lower()
    phone = data["phone"].strip()
    password = data["password"].strip()

    if len(full_name) < 3:
        return Response({"error": "Full name must be at least 3 characters"}, status=400)

    if User.objects.filter(username=email).exists():
        return Response({"error": "Email already exists"}, status=400)

    if not phone.isdigit() or len(phone) != 10:
        return Response({"error": "Phone number must be 10 digits"}, status=400)

    if len(password) < 6:
        return Response({"error": "Password must be at least 6 characters"}, status=400)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
    )

    Profile.objects.create(user=user, role="doctor")

    Doctor.objects.create(
        user=user,
        full_name=full_name,
        phone=phone,
        specialization=data.get("specialization"),
        qualification=data.get("qualification"),
        experience_years=data.get("experience_years"),
        clinic_name=data.get("clinic_name"),
        city=data.get("city"),
        consultation_fee=data.get("consultation_fee"),
        profile_image=request.FILES.get("profile_image"),
    )

    return Response(
        {"success": "Doctor registered successfully"},
        status=201,
    )


# =====================================================
# DOCTOR LOGIN (HTML + AJAX)
# =====================================================
@never_cache
def doctor_login(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/doctor/dashboard/")
        return render(request, "accounts/doctor_login.html")

    data = json.loads(request.body)
    email = data.get("email")
    password = data.get("password")

    user = authenticate(username=email, password=password)

    if user is None:
        return JsonResponse({"success": False, "error": "Invalid credentials"}, status=400)

    if user.profile.role != "doctor":
        return JsonResponse({"success": False, "error": "Doctor access only"}, status=400)

    login(request, user)

    return JsonResponse({"success": True, "redirect_url": "/doctor/dashboard/"})


# =====================================================
# PATIENT LOGIN
# =====================================================
@never_cache
@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def patient_login(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/patient/dashboard/")
        return render(request, "accounts/patient_login.html")

    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(username=email, password=password)

    if user is None:
        return Response({"success": False, "error": "Invalid credentials"}, status=400)

    if user.profile.role != "patient":
        return Response({"success": False, "error": "Patient access only"}, status=400)

    login(request, user)

    return Response({"success": True, "redirect_url": "/patient/dashboard/"})


# =====================================================
# PATIENT REGISTER API
# =====================================================
@extend_schema(
    request=PatientRegisterSerializer,
    responses={200: dict},
)
@api_view(["POST"])
@permission_classes([AllowAny])
@transaction.atomic
def patient_register_api(request):
    serializer = PatientRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    full_name = data["full_name"].strip()
    email = data["email"].strip().lower()
    phone = data["phone"].strip()
    password = data["password"].strip()
    gender = data["gender"]
    dob = data["date_of_birth"]
    city = data["city"].strip()

    errors = {}

    if len(full_name) < 3:
        errors["full_name"] = "Name must be at least 3 characters"

    if User.objects.filter(username=email).exists():
        errors["email"] = "Email already registered"

    phone_clean = phone.replace("+", "").replace(" ", "")
    if not phone_clean.isdigit() or len(phone_clean) < 10:
        errors["phone"] = "Enter valid phone number"

    if len(password) < 6:
        errors["password"] = "Password must be at least 6 characters"

    if errors:
        return Response({"errors": errors}, status=400)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
    )

    profile, _ = Profile.objects.get_or_create(user=user)
    profile.role = "patient"
    profile.save()

    Patient.objects.create(
        user=user,
        full_name=full_name,
        phone=phone_clean,
        gender=gender,
        date_of_birth=dob,
        city=city,
    )

    return Response({"success": True, "message": "Patient registered successfully"})


# =====================================================
# LOGOUT
# =====================================================
def logout_view(request):
    logout(request)
    return redirect("/")
# =====================================================
# PATIENT LOGIN (HTML + AJAX)
# =====================================================
import json
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render

def patient_login(request):

    # 🔹 Get ?next= from URL (GET request)
    next_from_get = request.GET.get("next")

    if request.method == "POST":
        data = json.loads(request.body)

        email = data.get("email")
        password = data.get("password")

        # 🔹 Get next from POST body
        next_from_post = data.get("next")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # 🔥 Priority: POST next > GET next > dashboard
            redirect_url = next_from_post or next_from_get or "/patient/dashboard/"

            return JsonResponse({
                "success": True,
                "redirect_url": redirect_url
            })

        return JsonResponse({
            "success": False,
            "error": "Invalid email or password"
        })

    return render(request, "accounts/patient_login.html")