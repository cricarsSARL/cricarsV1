from datetime import date
from .models import User, Car, Host
from django import forms
from django.core.exceptions import ValidationError


class CarSearchForm(forms.Form):
    make = forms.CharField(max_length=100, required=False)
    model = forms.CharField(max_length=100, required=False)
    year = forms.IntegerField(required=False)
    available_from = forms.DateField(required=False)
    available_until = forms.DateField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        available_from = cleaned_data.get("available_from")
        available_until = cleaned_data.get("available_until")

        if available_from and available_until and available_from > available_until:
            raise forms.ValidationError(
                "Available from date must be before the available until date.")


class RegistrationForm(forms.Form):
    email = forms.EmailField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class LoginForm(forms.Form):
    # Changed to EmailField for better validation
    email = forms.EmailField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")

        user = User.objects.filter(email=email).first()
        if not user:
            raise forms.ValidationError(
                "No account found with this email address.")

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters long.")
        return password

# form for adding car for the hosts


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        exclude = ['owner']  # owner will be set in the view, not in the form
        widgets = {
            'last_maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'insurance_info': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Custom validation logic (mimicking your model's `clean` property)
        year = cleaned_data.get('year')
        mileage = cleaned_data.get('mileage')
        engine_capacity = cleaned_data.get('engine_capacity')
        number_of_seats = cleaned_data.get('number_of_seats')
        number_of_doors = cleaned_data.get('number_of_doors')
        pricePerDay = cleaned_data.get('pricePerDay')
        transmission = cleaned_data.get('transmission')
        fuel_type = cleaned_data.get('fuel_type')
        registration_number = cleaned_data.get('registration_number')
        last_maintenance_date = cleaned_data.get('last_maintenance_date')

        from django.core.exceptions import ValidationError
        from django.utils import timezone

        if year and year < 2000:
            self.add_error('year', "Year must be 2000 or later.")

        if mileage and mileage > 300000:
            self.add_error('mileage', "Mileage must be ≤ 300,000 km.")

        if engine_capacity is not None and engine_capacity <= 0:
            self.add_error('engine_capacity', "Engine capacity must be > 0.")

        if number_of_seats and number_of_seats <= 0:
            self.add_error('number_of_seats', "Number of seats must be > 0.")

        if number_of_doors and number_of_doors <= 0:
            self.add_error('number_of_doors', "Number of doors must be > 0.")

        if pricePerDay and pricePerDay <= 200:
            self.add_error('pricePerDay', "Price per day must be > 200.")

        if transmission and transmission not in ['manual', 'automatic']:
            self.add_error(
                'transmission', "Transmission must be 'manual' or 'automatic'.")

        if fuel_type and fuel_type not in ['petrol', 'diesel', 'electric']:
            self.add_error(
                'fuel_type', "Fuel type must be 'petrol', 'diesel', or 'electric'.")

        if not registration_number:
            self.add_error('registration_number',
                           "Registration number is required.")

        if last_maintenance_date and last_maintenance_date > timezone.now().date():
            self.add_error('last_maintenance_date',
                           "Date cannot be in the future.")


class HostRegistrationForm(forms.Form):
    email = forms.EmailField(
        max_length=150,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    company_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    additional_info = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        if password and len(password) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters long.")

        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            is_host=True,
            is_guest=False
        )

        Host.objects.create(
            user=user,
            company_name=data['company_name'],
            additional_info=data.get('additional_info', '')
        )

        return user


class HostLoginForm(forms.Form):
    email = forms.EmailField(
        max_length=150,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = User.objects.filter(email=email, is_host=True).first()
        if not user:
            raise forms.ValidationError(
                "No host account found with this email address.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            if user and not user.check_password(password):
                raise forms.ValidationError("Incorrect password.")
            if user and not user.is_host:
                raise forms.ValidationError(
                    "This account is not registered as a host.")

        return cleaned_data


class BookingForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and end:
            if start < date.today():
                raise ValidationError("Start date cannot be in the past.")
            if end < start:
                raise ValidationError("End date must be after start date.")
