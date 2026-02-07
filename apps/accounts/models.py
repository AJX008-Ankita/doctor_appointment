
from django.db import models
from django.contrib.auth.models import User


# ==============================
# Profile (Role)
# ==============================
class Profile(models.Model):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.email} - {self.role}"


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)

    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=150)
    experience_years = models.PositiveIntegerField()

    clinic_name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)

    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2)

    profile_image = models.ImageField(
        upload_to='doctors/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email




#================================
#patient
#==================================
from datetime import date

class Patient(models.Model):
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    city = models.CharField(max_length=100)

    @property
    def age(self):
        today = date.today()
        return (
            today.year - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )
