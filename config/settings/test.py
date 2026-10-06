"""Settings for the automated test suite."""

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = ["testserver"]

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
