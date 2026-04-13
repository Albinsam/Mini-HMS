from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Availability

class SignUpForm(UserCreationForm):
    # This choice field allows the user to select their role
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    
    # Adding email explicitly to make it mandatory for the notifications
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta(UserCreationForm.Meta):
        model = User
        # We add 'email' and 'role' to the existing fields (username, etc.)
        fields = UserCreationForm.Meta.fields + ('email', 'role')

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }