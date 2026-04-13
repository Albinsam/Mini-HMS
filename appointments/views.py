from django.db import transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.utils import timezone
from .models import Availability, Booking, User
from .forms import SignUpForm, AvailabilityForm
from .utils import create_calendar_event
import requests
from django.contrib import messages  # Import this!
import pytz
# The URL for your serverless-offline server
SERVERLESS_URL = "http://localhost:3000/dev/notify"

def home_redirect(request):
    if request.user.is_doctor:
        return redirect('doctor_dashboard')
    elif request.user.is_patient:
        return redirect('patient_dashboard')
    return redirect('login')  

@login_required
def book_appointment(request, slot_id):
    if request.method == 'POST':
        booking_success = False
        slot = get_object_or_404(Availability, id=slot_id)

        # Atomic transaction ensures no two people can book the same slot at the exact same millisecond
        with transaction.atomic():
            slot = Availability.objects.select_for_update().get(id=slot_id)
            if not slot.is_booked:
                Booking.objects.create(patient=request.user, doctor=slot.doctor, slot=slot)
                slot.is_booked = True
                slot.save()
                booking_success = True

        if booking_success:
            # 1. GET THE LOGGED-IN PATIENT'S EMAIL
            # We use the email saved during our updated signup process
            user_email = request.user.email if request.user.email else "albinsamthomas13@gmail.com"
            # Get the India timezone object
            indian_tz = pytz.timezone('Asia/Kolkata')
            
            # Convert the slot time to local India time
            local_time = slot.start_time.astimezone(indian_tz)
            # 2. TRIGGER GOOGLE CALENDAR
            try:
                create_calendar_event(
                    summary=f"Appt: {request.user.username} w/ Dr. {slot.doctor.username}",
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    attendee_email=user_email
                )
                print("--- GOOGLE CALENDAR EVENT CREATED ---")
            except Exception as e:
                print(f"Calendar error: {e}")

            # 3. TRIGGER SERVERLESS EMAIL (The Microservice Call)
            try:
                payload = {
                    "action": "BOOKING_CONFIRMATION",
                    "email": user_email,
                    "username": request.user.username,
                    "doctor": slot.doctor.username,
                    "time": local_time.strftime("%d %b %Y at %I:%M %p") # Prettier format for email
                }
                
                # Calling the Serverless Offline endpoint
                requests.post(SERVERLESS_URL, json=payload, timeout=8)
                print(f"--- SERVERLESS CALL SENT: BOOKING_CONFIRMATION to {user_email} ---")
                
            except Exception as e:
                print(f"Serverless email error: {e}")

            messages.success(request, "Appointment booked and confirmation email sent!")
        else:
            messages.error(request, "This slot has already been taken.")

        return redirect('patient_dashboard')
    
    return redirect('patient_dashboard')
@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        return redirect('patient_dashboard')
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.doctor = request.user
            slot.save()
            return redirect('doctor_dashboard')
    else:
        form = AvailabilityForm()
    slots = Availability.objects.filter(doctor=request.user).order_by('start_time')
    bookings = Booking.objects.filter(doctor=request.user).order_by('slot__start_time')
    return render(request, 'doctor_dashboard.html', {'slots': slots, 'bookings': bookings, 'form': form})

@login_required
def patient_dashboard(request):
    if not request.user.is_patient:
        return redirect('doctor_dashboard')
    available_slots = Availability.objects.filter(is_booked=False, start_time__gt=timezone.now()).select_related('doctor')
    return render(request, 'patient_dashboard.html', {'available_slots': available_slots})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save user details
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')
            user.email = form.cleaned_data.get('email') # Explicitly grab the email
            
            if role == 'doctor':
                user.is_doctor = True 
            elif role == 'patient':
                user.is_patient = True 
            user.save()

            # 1. ADD SUCCESS MESSAGE
            messages.success(request, f"Account created for {user.username}! You can now login.")
            
            # 2. TRIGGER SERVERLESS
            try:
                payload = {
                    "action": "SIGNUP_WELCOME",
                    "email": user.email,
                    "username": user.username
                }
                
                # Changed timeout to 5. 0 will fail, and 1 is often too fast for local serverless
                requests.post(SERVERLESS_URL, json=payload, timeout=5)
                print(f"--- SERVERLESS CALL SENT: SIGNUP_WELCOME to {user.email} ---")
                
            except Exception as e:
                # We print the error but don't stop the user from logging in
                print(f"Signup email connection error: {e}")

            return redirect('login')
        else:
            print(f"Form Errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') 
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})