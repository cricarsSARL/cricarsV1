from django.contrib.messages import get_messages
from django.urls import reverse
from django.test import TestCase, Client
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from .models import Car, User, Host, Guest

User = get_user_model()


def create_user(username='user1', password='testpass123', phone_number='0612345678', is_host=False, is_guest=False):
    return User.objects.create_user(
        username=username,
        password=password,
        phone_number=phone_number,
        is_host=is_host,
        is_guest=is_guest
    )


def create_host(username='host1', password='testpass123', company_name='HostCompany', additional_info='VIP Host'):
    user = create_user(username=username, password=password, is_host=True)
    return Host.objects.create(user=user, company_name=company_name, additional_info=additional_info)


def create_guest(username='guest1', password='testpass123', preferences='Eco-friendly cars'):
    user = create_user(username=username, password=password, is_guest=True)
    return Guest.objects.create(user=user, preferences=preferences)


class UserModelTest(TestCase):
    def test_create_user(self):
        user = create_user()
        self.assertEqual(user.username, 'user1')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.phone_number)
        self.assertFalse(user.is_host)
        self.assertFalse(user.is_guest)

    def test_create_host_profile(self):
        host = create_host()
        self.assertEqual(host.company_name, 'HostCompany')
        self.assertTrue(host.user.is_host)
        self.assertFalse(host.user.is_guest)

    def test_create_guest_profile(self):
        guest = create_guest()
        self.assertEqual(guest.preferences, 'Eco-friendly cars')
        self.assertTrue(guest.user.is_guest)
        self.assertFalse(guest.user.is_host)


class CarModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.valid_car_data = {
            'mark': 'Toyota',
            'model': 'Corolla',
            'year': 2022,
            'color': 'Red',
            'number_of_seats': 5,
            'fuel_type': 'petrol',
            'number_of_doors': 4,
            'engine_capacity': 1.8,
            'transmission': 'automatic',
            'mileage': 50000,
            'pricePerDay': 300,
            'owner': self.user,
            'availability_status': 'available',
            'registration_number': 'ABC-1234',
            'description': 'A well-maintained car.',
            'insurance_info': 'Full coverage',
            'last_maintenance_date': timezone.now().date() - timedelta(days=30),
            'air_conditioning': True,
            'has_gps': True
        }

    def test_valid_car_passes_clean(self):
        car = Car(**self.valid_car_data)
        try:
            car.clean  # Should not raise ValidationError
        except ValidationError:
            self.fail("Valid car data raised ValidationError unexpectedly.")

    def test_year_below_2000_raises_error(self):
        self.valid_car_data['year'] = 1999
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError) as ctx:
            car.clean
        self.assertIn("Year must be 2000 or later.", str(ctx.exception))

    def test_mileage_above_limit_raises_error(self):
        self.valid_car_data['mileage'] = 350000
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError) as ctx:
            car.clean
        self.assertIn(
            "Mileage must be less than or equal to 300,000 km.", str(ctx.exception))

    def test_invalid_transmission_raises_error(self):
        self.valid_car_data['transmission'] = 'semi-automatic'
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError) as ctx:
            car.clean
        self.assertIn(
            "Transmission must be either 'manual' or 'automatic'.", str(ctx.exception))

    def test_invalid_fuel_type_raises_error(self):
        self.valid_car_data['fuel_type'] = 'hybrid'
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError) as ctx:
            car.clean
        self.assertIn(
            "Fuel type must be either 'petrol', 'diesel', or 'electric'.", str(ctx.exception))

    def test_last_maintenance_date_in_future_raises_error(self):
        self.valid_car_data['last_maintenance_date'] = timezone.now(
        ).date() + timedelta(days=1)
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError) as ctx:
            car.clean
        self.assertIn(
            "Last maintenance date cannot be in the future.", str(ctx.exception))

    def test_price_per_day_too_low_raises_error(self):
        self.valid_car_data['pricePerDay'] = 150
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError) as ctx:
            car.clean
        self.assertIn("Price per day must be greater than 200.",
                      str(ctx.exception))

    def test_missing_registration_number_raises_error(self):
        self.valid_car_data['registration_number'] = ''
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError) as ctx:
            car.clean
        self.assertIn("Registration number is required.", str(ctx.exception))


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')
        self.home_url = reverse('home')

    def test_register_get_request_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_authenticated_user_redirected_to_home(self):
        user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone_number='0612345678'
        )
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertRedirects(response, self.home_url)

    def test_missing_fields_shows_error(self):
        response = self.client.post(self.url, {})
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("All fields are required", str(messages[0]))
        self.assertTemplateUsed(response, 'register.html')

    def test_passwords_do_not_match(self):
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password_confirm': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '0612345678'
        }
        response = self.client.post(self.url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Passwords do not match", str(messages[0]))
        self.assertTemplateUsed(response, 'register.html')

    def test_password_too_short(self):
        data = {
            'email': 'test@example.com',
            'password': 'short',
            'password_confirm': 'short',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '0612345678'
        }
        response = self.client.post(self.url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(
            "Password must be at least 8 characters long", str(messages[0]))
        self.assertTemplateUsed(response, 'register.html')

    def test_email_already_exists(self):
        User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User',
            phone_number='0612345678'
        )
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '0612345678'
        }
        response = self.client.post(self.url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Email already exists", str(messages[0]))
        self.assertTemplateUsed(response, 'register.html')

    def test_successful_registration(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '0612345678'
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.home_url)
        self.assertTrue(User.objects.filter(
            email='newuser@example.com').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Registration successful!", str(messages[0]))


class HostViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Guest user (not a host yet)
        self.guest_user = User.objects.create_user(
            email='guest@example.com',
            password='password123',
            first_name='Guest',
            last_name='User',
            phone_number='0612345678',
            is_guest=True
        )

        # Host user
        self.host_user = User.objects.create_user(
            email='host@example.com',
            password='password123',
            first_name='Host',
            last_name='User',
            phone_number='0698765432',
            is_host=True
        )
        Host.objects.create(user=self.host_user, company_name='TestCo')

    def test_become_host_get_redirects_if_not_authenticated(self):
        response = self.client.get(reverse('become_host'))
        self.assertRedirects(response, reverse('login'))

    def test_become_host_get_authenticated(self):
        self.client.force_login(self.guest_user)
        response = self.client.get(reverse('become_host'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'become_host.html')

    def test_become_host_post_creates_host_profile(self):
        self.client.force_login(self.guest_user)
        response = self.client.post(reverse('become_host'), {
            'company_name': 'New Host Inc',
            'additional_info': 'Test company'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.guest_user.refresh_from_db()
        self.assertTrue(self.guest_user.is_host)
        self.assertFalse(self.guest_user.is_guest)
        self.assertTrue(Host.objects.filter(user=self.guest_user).exists())

    def test_car_listing_redirects_if_not_authenticated(self):
        response = self.client.get(reverse('car_listing'))
        self.assertRedirects(response, reverse('login'))

    def test_car_listing_blocks_non_host(self):
        self.client.force_login(self.guest_user)
        response = self.client.get(reverse('car_listing'))
        self.assertRedirects(response, reverse('home'))

    def test_car_listing_shows_host_cars(self):
        self.client.force_login(self.host_user)
        Car.objects.create(
            mark='Toyota',
            model='Corolla',
            year=2020,
            color='Blue',
            number_of_seats=5,
            fuel_type='petrol',
            number_of_doors=4,
            engine_capacity=1.6,
            transmission='manual',
            mileage=15000,
            pricePerDay=400,
            owner=self.host_user,
            registration_number='XYZ123',
        )
        response = self.client.get(reverse('car_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_listing.html')
        self.assertContains(response, 'Toyota')


class BecomeHostViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('become_host')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone_number='0612345678'
        )

    def test_get_request_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cars/become_host.html')

    def test_get_request_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cars/become_host.html')

    def test_post_request_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, 'cars/become_host_success.html')
        # Refresh user from database to get updated values
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_host)

    def test_post_request_unauthenticated(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(response.status_code, 302)
