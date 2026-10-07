from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = None
    last_name = None

    def get_full_name(self):
        return ""

    def get_short_name(self):
        return ""
