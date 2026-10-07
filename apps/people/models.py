from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel


class NaturalPerson(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="natural_person")
    full_name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=True, null=True)

    @property
    def age(self):
        if self.birth_date is None:
            return None

        today = timezone.localdate()
        birthday_has_passed = (today.month, today.day) >= (
            self.birth_date.month,
            self.birth_date.day,
        )

        return today.year - self.birth_date.year - (not birthday_has_passed)

    def __str__(self):
        return self.full_name
