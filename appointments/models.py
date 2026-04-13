from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Custom User Model to handle Roles [cite: 14, 20, 32]
class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)

# 2. Availability model for Doctors [cite: 18, 34]
class Availability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_doctor': True})
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False) # Once booked, it must be blocked [cite: 27]

    def __str__(self):
        return f"{self.doctor.username}: {self.start_time}"

# 3. Booking model for Patients [cite: 45]
class Booking(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_patient': True})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_bookings')
    slot = models.OneToOneField(Availability, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)