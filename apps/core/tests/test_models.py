from django.db import connection, models
from django.test import SimpleTestCase, TransactionTestCase

from apps.core.models import (
    ActorStampedModel,
    BaseModel,
    SoftDeleteModel,
    TimeStampedModel,
)


class CoreTestModel(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "core"


class AbstractModelsTests(SimpleTestCase):
    def test_models_are_abstract(self):
        self.assertTrue(TimeStampedModel._meta.abstract)
        self.assertTrue(ActorStampedModel._meta.abstract)
        self.assertTrue(SoftDeleteModel._meta.abstract)
        self.assertTrue(BaseModel._meta.abstract)

    def test_base_model_combines_all_shared_fields_and_managers(self):
        field_names = {field.name for field in BaseModel._meta.fields}

        self.assertTrue({"created_at", "updated_at", "created_by", "updated_by", "deleted_at"}.issubset(field_names))
        self.assertEqual(BaseModel._meta.base_manager_name, "all_objects")
        self.assertEqual(BaseModel._meta.default_manager_name, "objects")

    def test_timestamp_fields_have_expected_behavior(self):
        created_at = TimeStampedModel._meta.get_field("created_at")
        updated_at = TimeStampedModel._meta.get_field("updated_at")

        self.assertTrue(created_at.auto_now_add)
        self.assertTrue(updated_at.auto_now)

    def test_actor_fields_store_optional_strings(self):
        created_by = ActorStampedModel._meta.get_field("created_by")
        updated_by = ActorStampedModel._meta.get_field("updated_by")

        self.assertEqual(created_by.max_length, 255)
        self.assertTrue(created_by.blank)
        self.assertTrue(created_by.null)
        self.assertFalse(created_by.editable)
        self.assertEqual(updated_by.max_length, 255)
        self.assertTrue(updated_by.blank)
        self.assertTrue(updated_by.null)
        self.assertFalse(updated_by.editable)


class CoreModelsIntegrationTests(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(CoreTestModel)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(CoreTestModel)
        super().tearDownClass()

    def test_timestamps_and_actors_are_persisted(self):
        record = CoreTestModel.objects.create(
            name="record",
            created_by="actor@example.com",
            updated_by="worker:sync-catalog",
        )

        self.assertIsNotNone(record.created_at)
        self.assertIsNotNone(record.updated_at)
        self.assertEqual(record.created_by, "actor@example.com")
        self.assertEqual(record.updated_by, "worker:sync-catalog")

    def test_instance_delete_hides_record_and_restore_recovers_it(self):
        record = CoreTestModel.objects.create(name="record")

        count, _ = record.delete()

        self.assertEqual(count, 1)
        self.assertFalse(CoreTestModel.objects.filter(pk=record.pk).exists())
        self.assertTrue(CoreTestModel.all_objects.filter(pk=record.pk).exists())

        restored = record.restore()

        self.assertEqual(restored, 1)
        self.assertTrue(CoreTestModel.objects.filter(pk=record.pk).exists())

    def test_queryset_delete_and_restore(self):
        record = CoreTestModel.objects.create(name="record")

        count, _ = CoreTestModel.objects.filter(pk=record.pk).delete()

        self.assertEqual(count, 1)
        self.assertFalse(CoreTestModel.objects.filter(pk=record.pk).exists())

        restored = CoreTestModel.all_objects.filter(pk=record.pk).restore()

        self.assertEqual(restored, 1)
        self.assertTrue(CoreTestModel.objects.filter(pk=record.pk).exists())

    def test_hard_delete_removes_record(self):
        record = CoreTestModel.objects.create(name="record")
        record_id = record.pk

        record.hard_delete()

        self.assertFalse(CoreTestModel.all_objects.filter(pk=record_id).exists())
