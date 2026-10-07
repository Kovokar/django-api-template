from django.db import models

from apps.core.models import ActorStampedModel, BaseModel, TimeStampedModel


class Country(TimeStampedModel, ActorStampedModel):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class State(TimeStampedModel, ActorStampedModel):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="states")
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["country", "code"], name="unique_state_code_per_country"),
            models.UniqueConstraint(fields=["country", "name"], name="unique_state_name_per_country"),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class City(TimeStampedModel, ActorStampedModel):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="cities")
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["state", "name"], name="unique_city_name_per_state"),
        ]

    def __str__(self):
        return f"{self.name} - {self.state.code}"


class BaseAddress(BaseModel):
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    postal_code = models.CharField(max_length=20)
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    complement = models.CharField(blank=True, max_length=255, null=True)
    neighborhood = models.CharField(max_length=150)

    class Meta:
        abstract = True
        base_manager_name = "all_objects"
        default_manager_name = "objects"

    @property
    def full_address(self):
        parts = [f"{self.street}, {self.number}"]

        if self.complement:
            parts.append(self.complement)

        parts.extend(
            [
                self.neighborhood,
                f"{self.city.name}/{self.city.state.code}",
                self.postal_code,
                self.city.state.country.code,
            ]
        )

        return " - ".join(parts)

    def __str__(self):
        return self.full_address


class NaturalPersonAddress(BaseAddress):
    natural_person = models.ForeignKey("people.NaturalPerson", on_delete=models.CASCADE, related_name="addresses")
