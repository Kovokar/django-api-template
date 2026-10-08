import os
from unittest.mock import patch

from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import User


class UserModelTests(TestCase):
    def test_custom_user_is_configured_for_email_login(self):
        self.assertIs(get_user_model(), User)
        self.assertEqual(User.USERNAME_FIELD, "email")
        self.assertEqual(User.REQUIRED_FIELDS, [])
        self.assertEqual(User._meta.pk.get_internal_type(), "BigAutoField")

    def test_user_contains_only_technical_identity_fields(self):
        user = User(email="user@example.com")

        for field_name in ("first_name", "last_name", "username"):
            with self.assertRaises(FieldDoesNotExist):
                User._meta.get_field(field_name)

        for field_name in ("email", "password", "is_active", "is_staff", "is_superuser"):
            self.assertIsNotNone(User._meta.get_field(field_name))

        self.assertEqual(user.get_full_name(), "")
        self.assertEqual(user.get_short_name(), "")

    def test_create_user_requires_email_and_authenticates_case_insensitively(self):
        user = User.objects.create_user(email="User@Example.COM", password="safe-password")

        self.assertEqual(user.email, "user@example.com")
        self.assertNotEqual(user.password, "safe-password")
        self.assertTrue(user.check_password("safe-password"))
        self.assertEqual(authenticate(email="USER@example.com", password="safe-password"), user)
        self.assertIsNone(authenticate(email="user@example.com", password="wrong-password"))

        with self.assertRaisesMessage(ValueError, "The email must be set"):
            User.objects.create_user(password="safe-password")

        with self.assertRaises(ValidationError):
            User.objects.create_user(email="not-an-email", password="safe-password")

    def test_email_is_unique_case_insensitively(self):
        User.objects.create_user(email="User@example.com", password="safe-password")

        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(email="user@example.com", password="safe-password")

    def test_create_superuser_sets_permission_flags(self):
        user = User.objects.create_superuser(email="admin@example.com", password="safe-password")

        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_createsuperuser_command_creates_initial_technical_user(self):
        with patch.dict(os.environ, {"DJANGO_SUPERUSER_PASSWORD": "safe-password"}):
            call_command(
                "createsuperuser",
                email="admin@example.com",
                interactive=False,
                verbosity=0,
            )

        user = User.objects.get(email="admin@example.com")

        self.assertTrue(user.check_password("safe-password"))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
