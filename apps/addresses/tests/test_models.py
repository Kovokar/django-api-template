from django.db import IntegrityError, transaction
from django.db.models import CASCADE, PROTECT
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase, TestCase

from apps.accounts.models import User
from apps.addresses.models import BaseAddress, City, Country, NaturalPersonAddress, State
from apps.people.models import NaturalPerson


class BaseAddressTests(SimpleTestCase):
    def test_base_address_is_abstract_and_reusable(self):
        self.assertTrue(BaseAddress._meta.abstract)

        field_names = {field.name for field in BaseAddress._meta.fields}

        self.assertTrue(
            {
                "city",
                "postal_code",
                "street",
                "number",
                "complement",
                "neighborhood",
            }.issubset(field_names)
        )


class GeographicModelsTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(code="BR", name="Brazil")
        self.state = State.objects.create(country=self.country, code="CE", name="Ceara")
        self.city = City.objects.create(state=self.state, name="Fortaleza")

    def test_geographic_hierarchy_and_string_representations(self):
        self.assertEqual(list(self.country.states.all()), [self.state])
        self.assertEqual(list(self.state.cities.all()), [self.city])
        self.assertEqual(str(self.country), "Brazil (BR)")
        self.assertEqual(str(self.state), "Ceara (CE)")
        self.assertEqual(str(self.city), "Fortaleza - CE")

    def test_state_code_and_name_are_unique_per_country(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            State.objects.create(country=self.country, code="CE", name="Other State")

        with self.assertRaises(IntegrityError), transaction.atomic():
            State.objects.create(country=self.country, code="XX", name="Ceara")

    def test_city_name_is_unique_per_state(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            City.objects.create(state=self.state, name="Fortaleza")

    def test_geographic_relations_are_protected(self):
        self.assertIs(State._meta.get_field("country").remote_field.on_delete, PROTECT)
        self.assertIs(City._meta.get_field("state").remote_field.on_delete, PROTECT)

        with self.assertRaises(ProtectedError):
            self.country.delete()

        with self.assertRaises(ProtectedError):
            self.state.delete()


class NaturalPersonAddressTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email="person-with-address@example.com",
            password="safe-password",
        )
        self.person = NaturalPerson.objects.create(user=user, full_name="Address Test Person")
        country = Country.objects.create(code="BR", name="Brazil")
        state = State.objects.create(country=country, code="CE", name="Ceara")
        self.city = City.objects.create(state=state, name="Fortaleza")

    def create_address(self, street, complement=None):
        return NaturalPersonAddress.objects.create(
            natural_person=self.person,
            city=self.city,
            postal_code="60000-000",
            street=street,
            number="10",
            complement=complement,
            neighborhood="Centro",
        )

    def test_person_can_have_one_or_many_addresses(self):
        first_address = self.create_address("First Street")

        self.assertEqual(list(self.person.addresses.all()), [first_address])

        second_address = self.create_address("Second Street")

        self.assertCountEqual(self.person.addresses.all(), [first_address, second_address])

    def test_address_relations_have_expected_delete_behaviors(self):
        person_relation = NaturalPersonAddress._meta.get_field("natural_person")
        city_relation = NaturalPersonAddress._meta.get_field("city")

        self.assertIs(person_relation.remote_field.on_delete, CASCADE)
        self.assertIs(city_relation.remote_field.on_delete, PROTECT)

    def test_full_address_contains_complete_geographic_hierarchy(self):
        address = self.create_address("Main Avenue", complement="Apartment 20")

        self.assertEqual(
            address.full_address,
            "Main Avenue, 10 - Apartment 20 - Centro - Fortaleza/CE - 60000-000 - BR",
        )
        self.assertEqual(str(address), address.full_address)

    def test_full_address_omits_empty_complement(self):
        address = self.create_address("Main Avenue")

        self.assertEqual(address.full_address, "Main Avenue, 10 - Centro - Fortaleza/CE - 60000-000 - BR")

    def test_city_cannot_be_deleted_while_linked_to_address(self):
        self.create_address("Protected City Street")

        with self.assertRaises(ProtectedError):
            self.city.delete()

    def test_soft_delete_address_does_not_delete_person(self):
        address = self.create_address("Deleted Address Street")

        address.delete()

        self.assertFalse(NaturalPersonAddress.objects.filter(pk=address.pk).exists())
        self.assertTrue(NaturalPersonAddress.all_objects.filter(pk=address.pk).exists())
        self.assertTrue(NaturalPerson.objects.filter(pk=self.person.pk).exists())

    def test_soft_delete_person_does_not_implicitly_delete_addresses(self):
        address = self.create_address("Preserved Address Street")

        self.person.delete()

        self.assertTrue(NaturalPersonAddress.objects.filter(pk=address.pk).exists())

    def test_hard_delete_person_cascades_to_addresses(self):
        address = self.create_address("Cascaded Address Street")
        address_id = address.pk

        self.person.hard_delete()

        self.assertFalse(NaturalPersonAddress.all_objects.filter(pk=address_id).exists())
