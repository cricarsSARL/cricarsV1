from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core import mail
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from myapp.models import Car

User = get_user_model()


class HomeViewTests(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')


class LoginGuestView(TestCase):
    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')


class HostRegisterViewTests(TestCase):
    def test_register_host_view(self):
        response = self.client.get(reverse('host_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'host_register.html')


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@guest.com', password='testpass')

    def test_profile_view_authenticated(self):
        self.client.login(email='testuser@guest.com', password='testpass')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response, 'testuser@guest.com')

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, reverse('login'))


class CarListingViewTests(TestCase):
    def setUp(self):
        self.host_user = User.objects.create_user(
            email='host@test.com',
            password='testpass123',
            is_host=True
        )
        self.guest_user = User.objects.create_user(
            email='guest@test.com',
            password='testpass123'
        )
        self.car = Car.objects.create(
            mark='Toyota',
            model='Camry',
            year=2020,
            owner=self.host_user,
            color='Black',
            number_of_seats=5,
            fuel_type='petrol',
            number_of_doors=4,
            engine_capacity=2.5,
            transmission='automatic',
            mileage=50000,
            pricePerDay=250,
            registration_number='ABC123',
            availability_status='available'
        )

    def test_car_listing_authenticated_host(self):  # pass
        self.client.login(email='host@test.com', password='testpass123')
        response = self.client.get(reverse('car_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'car_listing.html')
        self.assertContains(response, self.car.model)

    def test_car_listing_authenticated_guest(self):  # pass
        self.client.login(email='guest@test.com', password='testpass123')
        response = self.client.get(reverse('car_listing'))
        self.assertRedirects(response, reverse('home'))

    def test_car_listing_unauthenticated(self):  # pass
        response = self.client.get(reverse('car_listing'))
        self.assertRedirects(response, reverse('login'))


class dashboardViewTests(TestCase):
    def setUp(self):
        self.host_user = User.objects.create_user(
            email='host@test.com',
            password='testpass123',
            is_host=True
        )
        self.guest_user = User.objects.create_user(
            email='guest@test.com',
            password='testpass123',
            is_guest=True)

    def test_dashboard_authenticated_host(self):
        self.client.login(email='host@test.com', password='testpass123')
        response = self.client.get(reverse('dashboard'))


class RegisterViewTests(TestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.valid_data = {
            'email': 'newuser@example.com',
            'password': 'securePassword123',
            'password_confirm': 'securePassword123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '0612345678'
        }

    def test_register_success_sends_email_and_creates_inactive_user(self):
        response = self.client.post(self.register_url, self.valid_data)

        # Redirect to login page after registration
        self.assertRedirects(response, reverse('login'))

        # User is created
        user = User.objects.get(email='newuser@example.com')
        self.assertFalse(user.is_active)

        # Email is sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Activate your account', mail.outbox[0].subject)
        # contains activation link
        self.assertIn('http://', mail.outbox[0].body)

    def test_register_fails_with_mismatched_passwords(self):
        data = self.valid_data.copy()
        data['password_confirm'] = 'wrongpass'
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")
        self.assertEqual(User.objects.count(), 0)

    def test_register_fails_with_existing_email(self):
        User.objects.create_user(
            email='newuser@example.com',
            password='whatever',
            first_name='Existing',
            last_name='User',
            phone_number='0600000000',
            is_active=True
        )
        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email already exists")
        self.assertEqual(User.objects.filter(
            email='newuser@example.com').count(), 1)

    def test_register_fails_with_missing_fields(self):
        data = self.valid_data.copy()
        data.pop('first_name')  # remove a required field
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All fields are required")
        self.assertEqual(User.objects.count(), 0)

    def test_register_fails_with_short_password(self):
        data = self.valid_data.copy()
        data['password'] = data['password_confirm'] = 'short'
        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Password must be at least 8 characters long")
        self.assertEqual(User.objects.count(), 0)


class ActivateViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='inactive@example.com',
            password='testpassword123',
            first_name='Inactive',
            last_name='User',
            phone_number='0600000000',
            is_active=False
        )

        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.activation_url = reverse('activate', kwargs={
            'uidb64': self.uid,
            'token': self.token
        })

    def test_activate_valid_token_activates_user(self):
        response = self.client.get(self.activation_url)

        self.assertRedirects(response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activate_invalid_token_does_not_activate(self):
        # Modify token to be invalid
        invalid_url = reverse('activate', kwargs={
            'uidb64': self.uid,
            'token': 'invalid-token'
        })
        response = self.client.get(invalid_url)

        self.assertRedirects(response, reverse('register'))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activate_invalid_uid_does_not_crash(self):
        invalid_url = reverse('activate', kwargs={
            'uidb64': 'invalid-uid',
            'token': self.token
        })
        response = self.client.get(invalid_url)

        self.assertRedirects(response, reverse('register'))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
