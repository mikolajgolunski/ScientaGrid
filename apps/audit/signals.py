from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog, ChangeHistory

# Models to track
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment
from apps.services.models import Service
from apps.institutions.models import Institution

# Add more models as needed
TRACKED_MODELS = [Infrastructure, Equipment, Service, Institution]


@receiver(post_save)
def log_creation_and_updates(sender, instance, created, **kwargs):
    """Log object creation and updates."""
    if sender not in TRACKED_MODELS:
        return

    if created:
        AuditLog.log_action(
            action_type='create',
            content_object=instance,
            description=f"Created {sender.__name__}: {instance}",
            category=sender.__name__.lower()
        )
    else:
        AuditLog.log_action(
            action_type='update',
            content_object=instance,
            description=f"Updated {sender.__name__}: {instance}",
            category=sender.__name__.lower()
        )


@receiver(post_delete)
def log_deletion(sender, instance, **kwargs):
    """Log object deletion."""
    if sender not in TRACKED_MODELS:
        return

    AuditLog.log_action(
        action_type='delete',
        content_object=None,  # Object no longer exists
        description=f"Deleted {sender.__name__}: {instance}",
        category=sender.__name__.lower()
    )


@receiver(pre_save)
def track_field_changes(sender, instance, **kwargs):
    """Track field-level changes."""
    if sender not in TRACKED_MODELS:
        return

    # Only track changes for existing objects
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    # Compare fields
    for field in instance._meta.get_fields():
        if field.concrete and not field.many_to_many and not field.one_to_many:
            if field.auto_created:
                continue

            field_name = field.name
            old_value = getattr(old_instance, field_name, None)
            new_value = getattr(instance, field_name, None)

            # Check if value changed
            if old_value != new_value:
                ChangeHistory.log_change(
                    content_object=instance,
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    change_type='update'
                )