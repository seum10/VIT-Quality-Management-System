from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class ProfileModelTest(TestCase):
    def test_profile_created_when_user_created(self):
        user = User.objects.create_user(
            username='student1',
            email='student1@vit.edu.au',
            password='Testpass123'
        )

        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.role, Profile.ROLE_STUDENT)

    def test_profile_string_representation(self):
        user = User.objects.create_user(
            username='qauser',
            email='qauser@vit.edu.au',
            password='Testpass123'
        )
        user.profile.role = Profile.ROLE_QA_OFFICER
        user.profile.save()

        self.assertIn('qauser', str(user.profile))


class AuthenticationViewTest(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_user_can_login(self):
        User.objects.create_user(
            username='student1',
            password='Testpass123'
        )

        response = self.client.post(reverse('login'), {
            'username': 'student1',
            'password': 'Testpass123',
        })

        self.assertEqual(response.status_code, 302)

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpass',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')