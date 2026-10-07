from datetime import date
from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from apps.accounts.models import User
from apps.people.models import NaturalPerson


class NaturalPersonModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="person-user", password="safe-password")

    def test_person_is_linked_to_technical_user(self):
        person = NaturalPerson.objects.create(user=self.user, full_name="Test Person")

        self.assertEqual(self.user.natural_person, person)
        self.assertEqual(str(person), "Test Person")

    def test_user_can_exist_without_person(self):
        self.assertFalse(hasattr(self.user, "natural_person"))

    def test_user_can_have_only_one_person(self):
        NaturalPerson.objects.create(user=self.user, full_name="First Person")

        with self.assertRaises(IntegrityError), transaction.atomic():
            NaturalPerson.objects.create(user=self.user, full_name="Second Person")

    def test_user_cannot_be_deleted_while_linked_to_person(self):
        NaturalPerson.objects.create(user=self.user, full_name="Protected Person")

        with self.assertRaises(ProtectedError):
            self.user.delete()

    def test_soft_delete_person_does_not_delete_user(self):
        person = NaturalPerson.objects.create(user=self.user, full_name="Deleted Person")

        person.delete()

        self.assertFalse(NaturalPerson.objects.filter(pk=person.pk).exists())
        self.assertTrue(NaturalPerson.all_objects.filter(pk=person.pk).exists())
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_age_is_calculated_from_birth_date(self):
        person = NaturalPerson(user=self.user, full_name="Person With Age", birth_date=date(2000, 10, 7))

        with patch("apps.people.models.timezone.localdate", return_value=date(2026, 10, 6)):
            self.assertEqual(person.age, 25)

        with patch("apps.people.models.timezone.localdate", return_value=date(2026, 10, 7)):
            self.assertEqual(person.age, 26)

    def test_age_is_unknown_without_birth_date(self):
        person = NaturalPerson(user=self.user, full_name="Person Without Age")

        self.assertIsNone(person.age)
