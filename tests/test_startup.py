from datetime import timedelta

from django.conf import settings
from django.test import SimpleTestCase


class StartupConfigurationTests(SimpleTestCase):
    def test_postgresql_is_the_default_database(self):
        database = settings.DATABASES["default"]

        self.assertEqual(database["ENGINE"], "django.db.backends.postgresql")
        self.assertTrue(database["NAME"])
        self.assertTrue(database["USER"])
        self.assertTrue(database["HOST"])
        self.assertTrue(database["PORT"])

    def test_django_rest_framework_is_installed(self):
        self.assertIn("rest_framework", settings.INSTALLED_APPS)

    def test_project_is_headless(self):
        disabled_apps = {
            "django.contrib.admin",
            "django.contrib.messages",
            "django.contrib.sessions",
            "django.contrib.staticfiles",
        }

        self.assertTrue(disabled_apps.isdisjoint(settings.INSTALLED_APPS))
        self.assertEqual(settings.TEMPLATES, [])
        self.assertEqual(
            settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"],
            ["rest_framework_simplejwt.authentication.JWTAuthentication"],
        )
        self.assertEqual(
            settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"],
            ["rest_framework.permissions.IsAuthenticated"],
        )
        self.assertEqual(
            settings.REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"],
            ["rest_framework.renderers.JSONRenderer"],
        )

    def test_jwt_policy_is_configured(self):
        self.assertIn("rest_framework_simplejwt.token_blacklist", settings.INSTALLED_APPS)
        self.assertFalse(settings.is_overridden("AUTHENTICATION_BACKENDS"))
        self.assertEqual(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"], timedelta(minutes=15))
        self.assertEqual(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"], timedelta(days=7))
        self.assertTrue(settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"])
        self.assertTrue(settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"])
        self.assertFalse(settings.SIMPLE_JWT["UPDATE_LAST_LOGIN"])
        self.assertEqual(settings.SIMPLE_JWT["ALGORITHM"], "HS256")
        self.assertEqual(settings.SIMPLE_JWT["AUTH_HEADER_TYPES"], ("Bearer",))

    def test_project_entrypoints_use_config(self):
        self.assertEqual(settings.ROOT_URLCONF, "config.urls")
        self.assertEqual(settings.WSGI_APPLICATION, "config.wsgi.application")

    def test_required_clients_are_importable(self):
        import psycopg
        import redis

        self.assertTrue(psycopg.__version__)
        self.assertTrue(redis.__version__)
