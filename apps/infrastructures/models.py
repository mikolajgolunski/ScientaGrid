from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from apps.institutions.models import Institution
from apps.locations.models import City
from apps.users.models import UserProfile


class Infrastructure(TranslatableModel):
    """Represents a research infrastructure facility."""

    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True),
        internal_comments=models.TextField(
            blank=True,
            help_text="Internal notes, not visible to external users"
        )
    )

    # Relationships
    institution = models.ForeignKey(
        Institution,
        on_delete=models.PROTECT,
        related_name='infrastructures'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='infrastructures',
        help_text="Primary location of the infrastructure"
    )

    # Non-translatable fields
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Reliability and status
    RELIABILITY_CHOICES = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Medium'),
        (4, 'High'),
        (5, 'Very High'),
    ]
    reliability = models.IntegerField(
        choices=RELIABILITY_CHOICES,
        default=3,
        help_text="Internal reliability rating (1-5)"
    )

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Has this infrastructure been verified by staff?"
    )

    # Metadata
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='infrastructures_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['translations__name']
        verbose_name_plural = "Infrastructures"

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f"Infrastructure {self.id}"

    @property
    def region(self):
        """Convenience property to get region."""
        return self.city.region

    @property
    def country(self):
        """Convenience property to get country."""
        return self.city.region.country


class ContactPerson(models.Model):
    """Represents a contact person for an infrastructure (no user account)."""

    infrastructure = models.ForeignKey(
        Infrastructure,
        on_delete=models.CASCADE,
        related_name='contact_persons'
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=150, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)

    is_primary = models.BooleanField(
        default=False,
        help_text="Is this the primary contact person?"
    )

    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this contact"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', 'last_name', 'first_name']
        verbose_name_plural = "Contact Persons"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.infrastructure.name})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"