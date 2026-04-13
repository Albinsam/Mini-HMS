from django.contrib import admin
from .models import User, Availability, Booking

admin.site.register(User)
admin.site.register(Availability)
admin.site.register(Booking)