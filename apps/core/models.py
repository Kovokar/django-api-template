from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils import timezone

from apps.core.managers import AllObjectsManager, SoftDeleteManager


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActorStampedModel(models.Model):
    created_by = models.CharField(max_length=255, blank=True, null=True, editable=False)
    updated_by = models.CharField(max_length=255, blank=True, null=True, editable=False)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, db_index=True, null=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True
        base_manager_name = "all_objects"
        default_manager_name = "objects"

    def delete(self, using=None, keep_parents=False):
        if self.pk is None:
            raise ValueError(
                f"{self.__class__.__name__} object can't be deleted because "
                "its primary key is not set."
            )

        if self.deleted_at is not None:
            return 0, {}

        self.deleted_at = timezone.now()
        update_fields = ["deleted_at"]

        try:
            updated_at = self._meta.get_field("updated_at")
        except FieldDoesNotExist:
            pass
        else:
            if isinstance(updated_at, models.DateTimeField) and updated_at.auto_now:
                update_fields.append("updated_at")

        self.save(using=using, update_fields=update_fields)

        return 1, {self._meta.label: 1}

    def restore(self, using=None):
        if self.pk is None:
            raise ValueError(
                f"{self.__class__.__name__} object can't be restored because "
                "its primary key is not set."
            )

        if self.deleted_at is None:
            return 0

        self.deleted_at = None
        update_fields = ["deleted_at"]

        try:
            updated_at = self._meta.get_field("updated_at")
        except FieldDoesNotExist:
            pass
        else:
            if isinstance(updated_at, models.DateTimeField) and updated_at.auto_now:
                update_fields.append("updated_at")

        self.save(using=using, update_fields=update_fields)

        return 1

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)


class BaseModel(TimeStampedModel, ActorStampedModel, SoftDeleteModel):
    class Meta:
        abstract = True
        base_manager_name = "all_objects"
        default_manager_name = "objects"
