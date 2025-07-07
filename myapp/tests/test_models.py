from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from myapp.models import User, Car, Host, Guest
from datetime import date, timedelta


def create_user(email='user1@email.test', password='testpass123', phone_number='0612345678', is_host=False, is_guest=False):
    return User.objects.create_user(
        email=email,
        password=password,
        phone_number=phone_number,
        is_host=is_host,
        is_guest=is_guest
    )


def create_host(email='host1@email.test', password='testpass123', company_name='HostCompany', additional_info='VIP Host'):
    user = create_user(email=email, password=password, is_host=True)
    return Host.objects.create(user=user, company_name=company_name, additional_info=additional_info)


def create_guest(email='guest1@email.test', password='testpass123', preferences='Eco-friendly cars'):
    user = create_user(email=email, password=password, is_guest=True)
    return Guest.objects.create(user=user, preferences=preferences)


class UserModelTest(TestCase):
    def test_create_user(self):
        user = create_user()
        self.assertEqual(user.email, 'user1@email.test')
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

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="owner@example.com", password="testpass123")
        cls.valid_car_data = {
            "mark": "Toyota",
            "model": "Corolla",
            "year": 2021,
            "color": "Red",
            "number_of_seats": 5,
            "fuel_type": "petrol",
            "number_of_doors": 4,
            "engine_capacity": 1.8,
            "transmission": "manual",
            "mileage": 50000,
            "pricePerDay": 300,
            "owner": cls.owner,
            "availability_status": "available",
            "registration_number": "ABC123XYZ",
            "last_maintenance_date": date.today(),
        }

    def test_valid_car_passes_clean(self):
        """Test that a valid car instance does not raise a ValidationError."""
        car = Car(**self.valid_car_data)
        try:
            car.clean
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

    def test_invalid_year_raises_error(self):
        self.valid_car_data["year"] = 1999
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError):
            car.clean

    def test_excessive_mileage_raises_error(self):
        self.valid_car_data["mileage"] = 400000
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError):
            car.clean

    def test_negative_engine_capacity_raises_error(self):
        self.valid_car_data["engine_capacity"] = -1
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError):
            car.clean

    def test_low_price_per_day_raises_error(self):
        self.valid_car_data["pricePerDay"] = 100
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError):
            car.clean

    def test_future_maintenance_date_raises_error(self):
        self.valid_car_data["last_maintenance_date"] = date.today(
        ) + timedelta(days=1)
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError):
            car.clean

    def test_invalid_transmission_raises_error(self):
        self.valid_car_data["transmission"] = "semi-auto"
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError):
            car.clean

    def test_invalid_fuel_type_raises_error(self):
        self.valid_car_data["fuel_type"] = "water"
        car = Car(**self.valid_car_data)
        with self.assertRaises(ValidationError):
            car.clean
