from .models import Booking
from django.contrib import admin
from .models import Car, User, Booking


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('mark', 'model', 'year',
                    'pricePerDay', 'availability_status')
    list_filter = ('availability_status', 'fuel_type',
                   'transmission', 'air_conditioning', 'has_gps')
    search_fields = ('mark', 'model', 'registration_number')
    ordering = ('-year',)


admin.site.register(User)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['car', 'guest', 'start_date', 'end_date', 'created_at']
    list_filter = ['start_date', 'end_date']
