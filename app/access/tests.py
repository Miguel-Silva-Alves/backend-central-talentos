from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from datetime import timedelta
from django.utils import timezone

from access.models import User, Token, GoogleAuthentication, RecoveryPassword
from access.factories import (
    UserFactory, TokenFactory,
    GoogleAuthenticationFactory, RecoveryPasswordFactory
)

from passlib.hash import django_pbkdf2_sha256 as handler


class UserViewSetTest(APITestCase):

    def setUp(self):
        self.user = UserFactory(password=handler.hash('testpassword'))
        self.token = TokenFactory(user=self.user)

        self.api_key_header = {'HTTP_X_API_KEY': 'j6Q04H4J2pTOCMTLWr9bDpBQerrxU9U'}
        self.token_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token.token}'}

        self.user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123"
        }

        self.user_data_no_password = {
            "email": "anotheruser@example.com"
        }

        # mock require_x_api_key
        self.patch_x_api_key = patch('common.token.TokenValidator.require_x_api_key', lambda f: f)
        self.patch_x_api_key.start()

        # mock require_token
        self.patch_require_token = patch('common.token.TokenValidator.require_token', lambda f: f)
        self.patch_require_token.start()

    def tearDown(self):
        self.patch_x_api_key.stop()
        self.patch_require_token.stop()

    # LIST
    def test_list_users_success(self):
        UserFactory.create_batch(3)

        url = reverse('user-list')
        res = self.client.get(url, **self.api_key_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["users"]), 4)

    # RETRIEVE
    def test_retrieve_user_success(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})
        res = self.client.get(url, **self.api_key_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['user']['email'], self.user.email)

    def test_retrieve_user_not_found(self):
        url = reverse('user-detail', kwargs={'pk': 9999})
        res = self.client.get(url, **self.api_key_header)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.data['message'], 'user not found')

    # CREATE
    def test_create_user_success(self):
        url = reverse('user-list')
        res = self.client.post(url, self.user_data, format='json', **self.api_key_header)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(User.objects.count(), 2)

        created = User.objects.get(email='newuser@example.com')
        self.assertTrue(handler.verify('newpassword123', created.password))

    def test_create_user_missing_password(self):
        url = reverse('user-list')
        res = self.client.post(url, self.user_data_no_password, format='json', **self.api_key_header)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data['message'], 'password is required')

    # UPDATE
    def test_update_user_success(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})

        self.client.force_authenticate(user=self.user)
        res = self.client.patch(url, {'email': 'updated@example.com'}, format='json', **self.token_header)

        self.assertEqual(res.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')

    # DELETE
    def test_destroy_user_success(self):
        url = reverse('user-detail', kwargs={'pk': self.user.pk})

        self.client.force_authenticate(user=self.user)
        res = self.client.delete(url, **self.token_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    # LOGIN
    def test_login_success(self):
        url = reverse('user-login')
        res = self.client.post(url, {"email": self.user.email, "password": "testpassword"},
                               format='json', **self.api_key_header)

        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertIn("expires_at", res.data)

    def test_login_user_not_found(self):
        url = reverse('user-login')
        res = self.client.post(url, {"email": "x@x.com", "password": "test"},
                               format='json', **self.api_key_header)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data['message'], 'User with given email does not exist.')

    # GOOGLE LOGIN
    def test_login_google_success_new_user(self):
        url = reverse('user-login-google')
        data = {"email": "g1@example.com", "client_id": "c", "sid": "s"}

        res = self.client.post(url, data, format='json', **self.api_key_header)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(GoogleAuthentication.objects.count(), 1)

    # PASSWORD RESET REQUEST
    def test_request_password_reset_success(self):
        url = reverse('user-request-password-reset')
        res = self.client.post(url, {"email": self.user.email},
                               format='json', **self.api_key_header)

        self.assertEqual(res.status_code, 200)
        self.assertIn("Código de recuperação gerado", res.data["detail"])
        self.assertTrue(RecoveryPassword.objects.filter(user=self.user).exists())

    # PASSWORD RESET
    def test_reset_password_success(self):
        rec = RecoveryPasswordFactory(user=self.user)

        url = reverse('user-reset-password')
        data = {"email": self.user.email, "code": rec.code, "new_password": "nova123"}

        res = self.client.post(url, data, format='json', **self.api_key_header)

        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(handler.verify("nova123", self.user.password))

        rec.refresh_from_db()
        self.assertFalse(rec.is_active)
