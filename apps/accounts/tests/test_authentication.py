from django.test import TestCase
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User


class ProtectedView(APIView):
    def get(self, request):
        return Response({"user_id": request.user.pk})


class JWTAuthenticationTests(TestCase):
    token_url = "/api/v1/auth/token/"
    refresh_url = "/api/v1/auth/token/refresh/"

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="User@example.com",
            password="safe-password",
        )

    def obtain_tokens(self, email="user@example.com", password="safe-password"):
        return self.client.post(self.token_url, {"email": email, "password": password}, format="json")

    def test_login_accepts_email_case_insensitively(self):
        response = self.obtain_tokens(email="user@EXAMPLE.COM")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {"access", "refresh"})

    def test_login_rejects_legacy_login_field(self):
        response = self.client.post(
            self.token_url,
            {"login": "user@example.com", "password": "safe-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_login_rejects_invalid_credentials_and_inactive_users_generically(self):
        wrong_password = self.obtain_tokens(password="wrong-password")
        missing_user = self.obtain_tokens(email="missing@example.com")
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        inactive_user = self.obtain_tokens()

        self.assertEqual(wrong_password.status_code, 401)
        self.assertEqual(missing_user.status_code, 401)
        self.assertEqual(inactive_user.status_code, 401)
        self.assertEqual(wrong_password.data, missing_user.data)
        self.assertEqual(missing_user.data, inactive_user.data)

    def test_access_token_authenticates_a_protected_view(self):
        access = self.obtain_tokens().data["access"]
        factory = APIRequestFactory()
        request = factory.get("/protected/", HTTP_AUTHORIZATION=f"Bearer {access}")

        response = ProtectedView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"user_id": self.user.pk})

    def test_protected_view_rejects_missing_and_invalid_tokens(self):
        factory = APIRequestFactory()

        missing = ProtectedView.as_view()(factory.get("/protected/"))
        invalid = ProtectedView.as_view()(
            factory.get("/protected/", HTTP_AUTHORIZATION="Bearer invalid-token")
        )

        self.assertEqual(missing.status_code, 401)
        self.assertEqual(invalid.status_code, 401)

    def test_refresh_rotation_returns_new_pair_and_blacklists_previous_refresh(self):
        original_refresh = self.obtain_tokens().data["refresh"]

        response = self.client.post(self.refresh_url, {"refresh": original_refresh}, format="json")
        reuse = self.client.post(self.refresh_url, {"refresh": original_refresh}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {"access", "refresh"})
        self.assertNotEqual(response.data["refresh"], original_refresh)
        self.assertEqual(reuse.status_code, 401)

    def test_tokens_only_expose_the_stable_user_identifier(self):
        access = AccessToken(self.obtain_tokens().data["access"])

        self.assertEqual(access["user_id"], str(self.user.pk))
        self.assertNotIn("email", access)
        self.assertNotIn("username", access)
