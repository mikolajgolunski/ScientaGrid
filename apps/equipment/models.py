from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from apps.infrastructures.models import Infrastructure


class Equipment(TranslatableModel):
    """Represents physical equipment/devices at research infrastructures."""

    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True),
        technical_details=models.TextField(
            blank=True,
            help_text="Technical specifications and capabilities"
        ),
        sample_requirements=models.TextField(
            blank=True,
            help_text="Sample preparation requirements and constraints"
        ),
        internal_notes=models.TextField(
            blank=True,
            help_text="Internal notes, not visible to external users"
        )
    )

    # Relationships
    infrastructure = models.ForeignKey(
        Infrastructure,
        on_delete=models.CASCADE,
        related_name='equipment'
    )

    # Non-translatable fields
    manufacturer = models.CharField(max_length=200, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    year_of_purchase = models.IntegerField(
        null=True,
        blank=True,
        help_text="Year the equipment was purchased"
    )

    # Status
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('out_of_order', 'Out of Order'),
        ('reserved', 'Reserved'),
        ('decommissioned', 'Decommissioned'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='operational'
    )

    is_available = models.BooleanField(
        default=True,
        help_text="Is equipment currently available for use?"
    )

    # Quality indicators
    CONDITION_CHOICES = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]
    condition = models.IntegerField(
        choices=CONDITION_CHOICES,
        default=3,
        help_text="Physical condition of the equipment"
    )

    requires_training = models.BooleanField(
        default=False,
        help_text="Does this equipment require special training?"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Taxonomy
    technology_domains = models.ManyToManyField(
        'taxonomy.TechnologyDomain',
        blank=True,
        related_name='equipment'
    )
    tags = models.ManyToManyField(
        'taxonomy.Tag',
        blank=True,
        related_name='equipment'
    )

    class Meta:
        ordering = ['infrastructure_id', 'id']
        verbose_name_plural = "Equipment"

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or f"Equipment {self.id}"
        if self.model_number:
            return f"{name} ({self.model_number})"
        return name

    @property
    def institution(self):
        """Convenience property to get institution."""
        return self.infrastructure.institution

    @property
    def city(self):
        """Convenience property to get city."""
        return self.infrastructure.city

    @property
    def full_location(self):
        """Get full location string."""
        return f"{self.infrastructure.name}, {self.city.name}"