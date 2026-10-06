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

    def test_project_entrypoints_use_config(self):
        self.assertEqual(settings.ROOT_URLCONF, "config.urls")
        self.assertEqual(settings.WSGI_APPLICATION, "config.wsgi.application")

    def test_required_clients_are_importable(self):
        import psycopg
        import redis

        self.assertTrue(psycopg.__version__)
        self.assertTrue(redis.__version__)
