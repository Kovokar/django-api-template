import os
from unittest.mock import patch

from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import User


class UserModelTests(TestCase):
    def test_custom_user_is_configured_for_username_login(self):
        self.assertIs(get_user_model(), User)
        self.assertEqual(User.USERNAME_FIELD, "username")
        self.assertEqual(User._meta.pk.get_internal_type(), "BigAutoField")

    def test_user_contains_only_technical_identity_fields(self):
        user = User(username="technical-user")

        for field_name in ("first_name", "last_name"):
            with self.assertRaises(FieldDoesNotExist):
                User._meta.get_field(field_name)

        for field_name in ("username", "email", "password", "is_active", "is_staff", "is_superuser"):
            self.assertIsNotNone(User._meta.get_field(field_name))

        self.assertEqual(user.get_full_name(), "")
        self.assertEqual(user.get_short_name(), "")

    def test_create_user_hashes_password_and_authenticates_by_username(self):
        user = User.objects.create_user(username="technical-user", password="safe-password")

        self.assertNotEqual(user.password, "safe-password")
        self.assertTrue(user.check_password("safe-password"))
        self.assertEqual(authenticate(username="technical-user", password="safe-password"), user)
        self.assertIsNone(authenticate(username="technical-user", password="wrong-password"))

    def test_create_superuser_sets_permission_flags(self):
        user = User.objects.create_superuser(username="admin", password="safe-password")

        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_createsuperuser_command_creates_initial_technical_user(self):
        with patch.dict(os.environ, {"DJANGO_SUPERUSER_PASSWORD": "safe-password"}):
            call_command(
                "createsuperuser",
                username="bootstrap-admin",
                email="admin@example.com",
                interactive=False,
                verbosity=0,
            )

        user = User.objects.get(username="bootstrap-admin")

        self.assertTrue(user.check_password("safe-password"))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
