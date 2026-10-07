from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils import timezone


def _update_timestamp_if_available(model, values, timestamp):
    try:
        field = model._meta.get_field("updated_at")
    except FieldDoesNotExist:
        return

    if isinstance(field, models.DateTimeField) and field.auto_now:
        values["updated_at"] = timestamp


class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        return self.filter(deleted_at__isnull=False)

    def delete(self):
        timestamp = timezone.now()
        values = {"deleted_at": timestamp}
        _update_timestamp_if_available(self.model, values, timestamp)
        count = self.active().update(**values)

        return count, {self.model._meta.label: count}

    def restore(self):
        timestamp = timezone.now()
        values = {"deleted_at": None}
        _update_timestamp_if_available(self.model, values, timestamp)

        return self.deleted().update(**values)

    def hard_delete(self):
        return super().delete()
