from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_redirect, name='home'), # Redirects based on role
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
]