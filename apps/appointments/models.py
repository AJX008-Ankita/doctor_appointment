from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
from django.utils import timezone
from apps.accounts.models import Doctor, Patient
  # adjust app name if different
from django.db import models
from django.utils import timezone

class Appointment(models.Model):

    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('checked_in', 'Checked In'),
        ('in_progress', 'Doctor Seeing'),
        ('completed', 'Completed'),
        ('cancelled_by_patient', 'Cancelled by Patient'),
        ('doctor_unavailable', 'Doctor Unavailable'),
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    availability = models.ForeignKey(
        'DoctorAvailability',
        on_delete=models.CASCADE,
        related_name="appointments",
        null=True,
        blank=True
    )

    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    patient_start_time = models.TimeField(null=True, blank=True)
    patient_end_time = models.TimeField(null=True, blank=True)

    reason = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    report_pdf = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_upcoming(self):
        return self.appointment_date >= timezone.now().date()

    def __str__(self):
        return f"{self.patient.full_name} - {self.doctor.full_name}"
#=================================
# Medical Record Model
#=================================
class MedicalNote(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="medical_note"
    )

    notes = models.TextField()
    prescription = models.TextField(blank=True)
    follow_up = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notes for {self.appointment}"
#==============================================
#docor available time model
#==============================================
from django.db import models
from django.conf import settings
from django.utils import timezone


class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="availability_slots"
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    capacity = models.PositiveIntegerField(
        default=5
    )  # Maximum patients per slot

    # ✅ Correct way (no auto_now_add here)
    created_at = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time} to {self.end_time}"