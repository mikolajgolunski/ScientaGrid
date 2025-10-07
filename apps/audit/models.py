from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.users.models import UserProfile
import json


class AuditLog(models.Model):
    """Records all significant actions in the system."""

    # Who performed the action
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    # When
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # What action
    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('export', 'Exported'),
        ('login', 'Logged In'),
        ('logout', 'Logged Out'),
        ('search', 'Searched'),
        ('other', 'Other'),
    ]
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        db_index=True
    )

    # What object (using generic foreign key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Additional details
    object_repr = models.CharField(
        max_length=200,
        help_text="String representation of the object at the time of action"
    )

    description = models.TextField(
        blank=True,
        help_text="Human-readable description of the action"
    )

    # Changed data (JSON)
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON representation of what changed"
    )

    # Context
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user"
    )

    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text="Browser user agent string"
    )

    # Categorization
    category = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Category for grouping logs (e.g., 'infrastructure', 'equipment')"
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} {self.get_action_type_display()} {self.object_repr} at {self.timestamp}"

    @classmethod
    def log_action(cls, action_type, user=None, content_object=None, description='',
                   changes=None, ip_address=None, user_agent=None, category=''):
        """
        Convenience method to create audit log entries.

        Usage:
            AuditLog.log_action(
                action_type='create',
                user=request.user,
                content_object=infrastructure,
                description='Created new infrastructure',
                changes={'name': 'New Name'},
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        """
        object_repr = str(content_object) if content_object else 'N/A'

        return cls.objects.create(
            user=user,
            action_type=action_type,
            content_object=content_object,
            object_repr=object_repr[:200],  # Truncate if too long
            description=description,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent[:255] if user_agent else '',  # Truncate if too long
            category=category
        )


class ChangeHistory(models.Model):
    """Detailed change history for specific models."""

    # What object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # When and who
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='change_history'
    )

    # What changed
    field_name = models.CharField(
        max_length=100,
        help_text="Name of the field that changed"
    )

    old_value = models.TextField(
        blank=True,
        help_text="Previous value (as string)"
    )

    new_value = models.TextField(
        blank=True,
        help_text="New value (as string)"
    )

    # Change type
    CHANGE_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    ]
    change_type = models.CharField(
        max_length=10,
        choices=CHANGE_TYPES,
        default='update'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Change Histories"
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.content_type} {self.object_id} - {self.field_name} changed at {self.timestamp}"

    @classmethod
    def log_change(cls, content_object, field_name, old_value, new_value, user=None, change_type='update'):
        """
        Convenience method to log field changes.

        Usage:
            ChangeHistory.log_change(
                content_object=infrastructure,
                field_name='name',
                old_value='Old Name',
                new_value='New Name',
                user=request.user
            )
        """
        return cls.objects.create(
            content_object=content_object,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else '',
            new_value=str(new_value) if new_value is not None else '',
            user=user,
            change_type=change_type
        )


class DataQualityMetric(models.Model):
    """Tracks data quality and completeness metrics."""

    # What object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Metrics
    completeness_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage of required fields filled (0-100)"
    )

    quality_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Overall quality score (0-100)"
    )

    # Details
    missing_fields = models.JSONField(
        default=list,
        help_text="List of missing required fields"
    )

    warnings = models.JSONField(
        default=list,
        help_text="List of data quality warnings"
    )

    # Specific checks
    has_description = models.BooleanField(default=False)
    has_contact = models.BooleanField(default=False)
    has_location = models.BooleanField(default=False)
    has_documentation = models.BooleanField(default=False)
    has_pricing = models.BooleanField(default=False)
    has_access_conditions = models.BooleanField(default=False)

    # Tracking
    last_updated = models.DateTimeField(auto_now=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_updated']
        unique_together = [['content_type', 'object_id']]
        verbose_name_plural = "Data Quality Metrics"

    def __str__(self):
        return f"{self.content_type} {self.object_id} - Quality: {self.quality_score}%"

    @property
    def quality_level(self):
        """Get quality level as text."""
        if self.quality_score >= 90:
            return 'Excellent'
        elif self.quality_score >= 75:
            return 'Good'
        elif self.quality_score >= 50:
            return 'Fair'
        else:
            return 'Poor'

    @classmethod
    def calculate_for_object(cls, content_object):
        """
        Calculate and save quality metrics for an object.
        This is a basic implementation - customize based on your needs.
        """
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_model(content_object)

        # Calculate completeness (example logic)
        total_fields = 0
        filled_fields = 0
        missing_fields = []
        warnings = []

        # Get all fields
        for field in content_object._meta.get_fields():
            if field.concrete and not field.many_to_many and not field.one_to_many:
                # Skip auto fields
                if field.auto_created:
                    continue

                total_fields += 1
                value = getattr(content_object, field.name, None)

                if value is not None and value != '':
                    filled_fields += 1
                else:
                    if not field.blank:  # Required field
                        missing_fields.append(field.name)

        completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0

        # Check specific attributes (customize based on model)
        has_description = False
        has_contact = False
        has_location = False
        has_documentation = False
        has_pricing = False
        has_access_conditions = False

        if hasattr(content_object, 'description'):
            desc = getattr(content_object, 'description', None)
            has_description = bool(desc)

        if hasattr(content_object, 'contact_persons'):
            has_contact = content_object.contact_persons.exists()
        elif hasattr(content_object, 'email'):
            has_contact = bool(getattr(content_object, 'email', None))

        if hasattr(content_object, 'city'):
            has_location = bool(getattr(content_object, 'city', None))

        if hasattr(content_object, 'documents'):
            has_documentation = content_object.documents.filter(status='active').exists()

        if hasattr(content_object, 'pricing_policies'):
            has_pricing = content_object.pricing_policies.filter(is_active=True).exists()

        if hasattr(content_object, 'access_conditions'):
            has_access_conditions = content_object.access_conditions.filter(is_active=True).exists()

        # Calculate quality score (weighted)
        quality_checks = [
            (completeness, 0.4),  # 40% weight
            (100 if has_description else 0, 0.15),  # 15%
            (100 if has_contact else 0, 0.15),  # 15%
            (100 if has_location else 0, 0.1),  # 10%
            (100 if has_documentation else 0, 0.1),  # 10%
            (100 if (has_pricing and has_access_conditions) else 0, 0.1),  # 10%
        ]

        quality_score = sum(score * weight for score, weight in quality_checks)

        # Generate warnings
        if not has_description:
            warnings.append("Missing description")
        if not has_contact:
            warnings.append("Missing contact information")
        if not has_documentation:
            warnings.append("No documentation uploaded")

        # Create or update metric
        metric, created = cls.objects.update_or_create(
            content_type=ct,
            object_id=content_object.pk,
            defaults={
                'completeness_score': round(completeness, 2),
                'quality_score': round(quality_score, 2),
                'missing_fields': missing_fields,
                'warnings': warnings,
                'has_description': has_description,
                'has_contact': has_contact,
                'has_location': has_location,
                'has_documentation': has_documentation,
                'has_pricing': has_pricing,
                'has_access_conditions': has_access_conditions,
            }
        )

        return metric