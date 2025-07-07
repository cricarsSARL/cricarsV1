from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_host = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    # You can put first_name, last_name if you want them required on createsuperuser
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Host(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='host_profile')
    company_name = models.CharField(max_length=100)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Host: {self.user.username}"


class Guest(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='guest_profile')
    preferences = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Guest: {self.user.username}"


class Car(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
    ]

    mark = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=50)
    number_of_seats = models.IntegerField()
    fuel_type = models.CharField(max_length=50)
    number_of_doors = models.IntegerField()
    engine_capacity = models.DecimalField(max_digits=5, decimal_places=3)
    transmission = models.CharField(max_length=50)
    mileage = models.IntegerField()
    pricePerDay = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    registration_number = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='car_images/', null=True, blank=True)
    insurance_info = models.TextField(blank=True, null=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    air_conditioning = models.BooleanField(default=True)
    has_gps = models.BooleanField(default=False)

    def clean(self):
        """
        Custom validation for Car model fields.
        Raises ValidationError if any field is invalid.
        """
        if self.year is not None and self.year < 2000:
            raise ValidationError("Year must be 2000 or later.")
        if self.mileage is not None and self.mileage > 300000:
            raise ValidationError(
                "Mileage must be less than or equal to 300,000 km.")
        if self.engine_capacity is not None and self.engine_capacity <= 0:
            raise ValidationError("Engine capacity must be greater than 0.")
        if self.number_of_seats is not None and self.number_of_seats <= 0:
            raise ValidationError("Number of seats must be greater than 0.")
        if self.number_of_doors is not None and self.number_of_doors <= 0:
            raise ValidationError("Number of doors must be greater than 0.")
        if self.pricePerDay is not None and self.pricePerDay <= 200:
            raise ValidationError("Price per day must be greater than 200.")
        if self.transmission is not None and self.transmission not in ['manual', 'automatic']:
            raise ValidationError(
                "Transmission must be either 'manual' or 'automatic'.")
        if self.fuel_type is not None and self.fuel_type not in ['petrol', 'diesel', 'electric']:
            raise ValidationError(
                "Fuel type must be either 'petrol', 'diesel', or 'electric'.")
        if self.registration_number is None or not self.registration_number.strip():
            raise ValidationError("Registration number is required.")
        if self.last_maintenance_date and self.last_maintenance_date > timezone.now().date():
            raise ValidationError(
                "Last maintenance date cannot be in the future.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensures clean() is called before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mark} {self.model} ({self.year})"


class Booking(models.Model):
    car = models.ForeignKey(
        'Car', on_delete=models.CASCADE, related_name='bookings')
    # adjust based on your model
    guest = models.ForeignKey(
        'Guest', on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car} booked by {self.guest} from {self.start_date} to {self.end_date}"

    def total_days(self):
        return (self.end_date - self.start_date).days + 1

    def total_price(self):
        return self.total_days() * self.car.pricePerDay
