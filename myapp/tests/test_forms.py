# tests/test_forms.py
from datetime import timedelta
from django.test import TestCase
from myapp.forms import CarSearchForm, LoginForm, RegistrationForm, CarForm
from myapp.models import User
from django.utils import timezone


class CarSearchFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'available_from': '2025-05-01',
            'available_until': '2025-05-10'
        }
        form = CarSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_date_range(self):
        form_data = {
            'available_from': '2025-05-15',
            'available_until': '2025-05-10'
        }
        form = CarSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn(
            "Available from date must be before the available until date.", form.errors['__all__'])

    def test_empty_form_is_valid(self):
        form = CarSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_non_integer_year(self):
        form_data = {'year': 'twenty twenty'}
        form = CarSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('year', form.errors)

    def test_full_valid_form(self):
        form_data = {
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'available_from': '2025-05-01',
            'available_until': '2025-05-10'
        }
        form = CarSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_future_date_range(self):
        form_data = {
            'available_from': '2030-01-01',
            'available_until': '2030-01-05'
        }
        form = CarSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_same_start_end_date(self):
        form_data = {
            'available_from': '2025-06-01',
            'available_until': '2025-06-01'
        }
        form = CarSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_only_available_from(self):
        form_data = {'available_from': '2025-06-01'}
        form = CarSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_only_available_until(self):
        form_data = {'available_until': '2025-06-10'}
        form = CarSearchForm(data=form_data)
        self.assertTrue(form.is_valid())


class LoginFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_valid_login_form(self):
        form_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form_data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_short_password(self):
        form_data = {
            'email': 'test@example.com',
            'password': 'short'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)


class RegistrationFormTest(TestCase):
    def test_valid_registration_form(self):
        form_data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_passwords_dont_match(self):
        form_data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'confirm_password': 'differentpass'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('Passwords do not match.', form.errors['__all__'])

    def test_missing_fields(self):
        form_data = {
            'email': 'newuser@example.com'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertIn('confirm_password', form.errors)

    def test_invalid_email_format(self):
        form_data = {
            'email': 'invalid-email',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class CarFormTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'year': 2020,
            'mileage': 50000,
            'engine_capacity': 1.6,
            'number_of_seats': 4,
            'number_of_doors': 4,
            'pricePerDay': 300,
            'transmission': 'manual',
            'fuel_type': 'petrol',
            'registration_number': 'ABC-1234',
            'last_maintenance_date': timezone.now().date() - timedelta(days=10),
            'description': 'Nice car',
            'insurance_info': 'Valid insurance',
        }

    def test_valid_form(self):
        form = CarForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_year(self):
        data = self.valid_data.copy()
        data['year'] = 1999
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('year', form.errors)

    def test_future_maintenance_date(self):
        data = self.valid_data.copy()
        data['last_maintenance_date'] = timezone.now().date() + \
            timedelta(days=1)
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_maintenance_date', form.errors)

    def test_invalid_transmission(self):
        data = self.valid_data.copy()
        data['transmission'] = 'semi-auto'
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('transmission', form.errors)

    def test_invalid_fuel_type(self):
        data = self.valid_data.copy()
        data['fuel_type'] = 'hybrid'
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('fuel_type', form.errors)

    def test_missing_registration_number(self):
        data = self.valid_data.copy()
        data['registration_number'] = ''
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('registration_number', form.errors)

    def test_price_too_low(self):
        data = self.valid_data.copy()
        data['pricePerDay'] = 150
        form = CarForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('pricePerDay', form.errors)
