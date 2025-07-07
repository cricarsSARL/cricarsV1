from django.http import Http404
from django.core.validators import validate_email
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404, redirect, render
from typing import Dict, Any
from .models import Car, Host, Booking
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, authenticate, get_user_model, logout as auth_logout
from django.contrib import messages
from .forms import CarForm, HostRegistrationForm, HostLoginForm, BookingForm
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User

User = get_user_model()


MOROCCAN_CITIES = [
    'Casablanca',
    'Rabat',
    'Marrakech',
    'Fes',
    'Tangier'
]

# Home page view with car search functionality.


def home(request: HttpRequest) -> Any:
    """Home page view with car search functionality."""
    cars = Car.objects.all()
    filters = {
        'make': 'make__icontains',
        'model': 'model__icontains',
        'year': 'year',
        'location': 'location__iexact',
        'available_from': 'available_from__lte',
        'available_until': 'available_until__gte'
    }

    # Apply filters from GET parameters
    filter_params = {field: request.GET[param] for param,
                     field in filters.items() if request.GET.get(param)}
    cars = cars.filter(**filter_params)

    context: Dict[str, Any] = {
        'cars': cars,
        'cities': MOROCCAN_CITIES,
    }
    return render(request, 'home.html', context)

# Login view for user authentication.


def login(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_host:
                messages.error(
                    request, 'Please use the host login page if you are a host.')
                return render(request, 'login.html')
            auth_login(request, user)
            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method != 'POST':
        return render(request, 'register.html')

    required_fields = ['email', 'password',
                       'password_confirm', 'first_name', 'last_name', 'phone']
    data = {field: request.POST.get(field) for field in required_fields}

    if not all(data.values()):
        messages.error(request, "All fields are required")
        return render(request, 'register.html')

    if data['password'] != data['password_confirm']:
        messages.error(request, "Passwords do not match")
        return render(request, 'register.html')

    if len(data['password']) < 8:
        messages.error(request, "Password must be at least 8 characters long")
        return render(request, 'register.html')

    if User.objects.filter(email=data['email']).exists():
        messages.error(request, "Email already exists")
        return render(request, 'register.html')

    try:
        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone'],
            is_active=False,  # deactivate until email confirmation
            is_host=False
        )

        # Generate confirmation token and URL
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request)
        activation_link = reverse(
            'activate', kwargs={'uidb64': uid, 'token': token})
        activation_url = f"http://{current_site.domain}{activation_link}"

        # Send email with HTML content
        subject = "Activate your account"
        html_message = render_to_string('emails/activation_email.html', {
            'user': user,
            'activation_url': activation_url,
        })
        # Create plain text version by stripping HTML
        plain_message = strip_tags(html_message)

        # Send email with both HTML and plain text versions
        send_mail(
            subject=subject,
            message=plain_message,  # Plain text version
            from_email=None,
            recipient_list=[user.email],
            html_message=html_message  # HTML version
        )

        messages.success(
            request, "Registration successful! Please check your email to activate your account.")
        return redirect('login')

    except Exception as e:
        print(f"Registration error: {str(e)}")
        messages.error(request, "Registration error. Please try again.")
        return render(request, 'register.html')


def activate(request, uidb64, token):
    """Account activation view with detailed error handling"""

    # Decode the user ID
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
    except (TypeError, ValueError):
        messages.error(request, "Invalid activation link format.")
        return redirect('login')

    # Get the user
    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    # Check if user is already active
    if user.is_active:
        messages.info(request, "Your account is already activated.")
        return redirect('login')

    # Verify the token
    if default_token_generator.check_token(user, token):
        try:
            user.is_active = True
            user.save()
            messages.success(
                request,
                f"Welcome {user.first_name}! Your account has been activated successfully."
            )
            return redirect('login')
        except Exception as e:
            print(f"Error activating user {user.id}: {str(e)}")
            messages.error(
                request, "Error activating account. Please try again or contact support.")
            return redirect('login')
    else:
        messages.error(
            request, "Invalid or expired activation link. Please request a new activation email.")
        return redirect('login')


def become_host(request):
    """View to register as a host."""
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        additional_info = request.POST.get('additional_info')

        if not company_name:
            messages.error(request, "Company name is required.")
            return render(request, 'become_host.html')

        # Update user to host
        user = request.user
        user.is_host = True
        user.is_guest = False
        user.save()

        # Create Host profile
        Host.objects.create(
            user=user,
            company_name=company_name,
            additional_info=additional_info
        )

        messages.success(request, "You are now registered as a host.")
        return redirect('dashboard')  # or wherever you want to send them

    return render(request, 'become_host.html')

# View for host register


def host_register(request):
    if request.method == 'POST':
        form = HostRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Successfully registered as a host!")
            return redirect('dashboard')
    else:
        form = HostRegistrationForm()

    return render(request, 'host_register.html', {'form': form})


def host_login(request):
    """Handle host login."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = HostLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None and user.is_host:
                auth_login(request, user)
                next_url = request.GET.get('next', 'car_listing')
                return redirect(next_url)
            else:
                messages.error(
                    request, 'Invalid credentials or not a host account.')
    else:
        form = HostLoginForm()

    return render(request, 'host_login.html', {'form': form})


def car_listing(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_host:
        messages.error(request, "Access denied: Hosts only.")
        return redirect('home')

    cars = Car.objects.filter(owner=request.user)
    context = {
        'cars': cars
    }
    return render(request, 'car_listing.html', context)


@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_host:
        return redirect('car_listing')

    # If the user is a guest, show their dashboard
    context = {
        'user': request.user
    }
    return render(request, 'dashboard.html', context)


@login_required
def addcar(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.owner = request.user
            try:
                car.full_clean()  # Ensures model-level validation is also checked
                car.save()
                messages.success(request, 'Car added successfully.')
                # Replace with your actual car list URL name
                return redirect('car_list')
            except ValidationError as e:
                form.add_error(None, e.message)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CarForm()

    return render(request, 'addcar.html', {'form': form})


def profile(request):
    """User profile view."""
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    context = {
        'user': user
    }
    return render(request, 'profile.html', context)


def logout(request):
    """Handle user logout."""
    auth_logout(request)
    return redirect('home')


def car_list(request):
    """Display a list of all cars."""
    cars = Car.objects.all()
    return render(request, 'car_list.html', {'cars': cars})


def car_detail(request, car_id):
    """Display details for a specific car."""
    try:
        car = Car.objects.get(pk=car_id)
    except Car.DoesNotExist:
        messages.error(request, "Car not found.")
        return redirect('car_list')
    return render(request, 'car_detail.html', {'car': car})


@login_required
def book_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            Booking.objects.create(
                guest=request.user.guest_profile,  # Adjust as needed
                car=car,
                start_date=start_date,
                end_date=end_date,
            )
            messages.success(request, "Booking confirmed!")
            return redirect('home')
    else:
        form = BookingForm()

    return render(request, 'book_car.html', {'form': form, 'car': car})


def legal_view(request):
    return render(request, 'privacy_terms.html')
