from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Doctor, Patient, Profile

class DoctorRegisterSerializer(serializers.ModelSerializer):
    # User fields
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Doctor
        fields = [
            'full_name',
            'phone',
            'specialization',
            'qualification',
            'experience_years',
            'clinic_name',
            'city',
            'consultation_fee',
            'profile_image',
            'email',
            'password',
        ]

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # Create Profile
        Profile.objects.create(
            user=user,
            role='doctor'
        )

        # Create Doctor
        doctor = Doctor.objects.create(
            user=user,
            **validated_data
        )

        return doctor

class DoctorLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
class PatientRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Patient
        fields = [
            'full_name',
            'phone',
            'gender',
            'date_of_birth',
            'city',
            'email',
            'password',
        ]

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # Create Profile
        Profile.objects.create(
            user=user,
            role='patient'
        )

        # Create Patient
        patient = Patient.objects.create(
            user=user,
            **validated_data
        )

        return patient
class PatientLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
