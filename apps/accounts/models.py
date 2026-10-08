from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower

from apps.accounts.managers import AccountManager


class User(AbstractUser):
    first_name = None
    last_name = None
    username = None
    email = models.EmailField(unique=True)

    objects = AccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta(AbstractUser.Meta):
        constraints = [
            models.CheckConstraint(condition=~models.Q(email=""), name="accounts_user_email_not_empty"),
            models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_unique"),
        ]

    def get_full_name(self):
        return ""

    def get_short_name(self):
        return ""
