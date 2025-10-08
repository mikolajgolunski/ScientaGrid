from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from apps.equipment.models import Equipment


class Service(TranslatableModel):
    """Represents a service/capability that can be offered by equipment."""

    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True),
        methodology=models.TextField(
            blank=True,
            help_text="Description of the methodology used"
        ),
        typical_applications=models.TextField(
            blank=True,
            help_text="Common research applications for this service"
        ),
        deliverables=models.TextField(
            blank=True,
            help_text="What the researcher receives (data format, reports, etc.)"
        )
    )

    # Non-translatable fields
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Internal service code for reference"
    )

    # Service characteristics
    typical_turnaround_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Typical number of days to complete the service"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Is this service currently offered?"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Taxonomy
    technology_domains = models.ManyToManyField(
        'taxonomy.TechnologyDomain',
        blank=True,
        related_name='services'
    )
    tags = models.ManyToManyField(
        'taxonomy.Tag',
        blank=True,
        related_name='services'
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or f"Service {self.id}"
        if self.code:
            return f"{name} ({self.code})"
        return name


class EquipmentService(models.Model):
    """
    Many-to-many relationship between Equipment and Service.
    Allows storing additional information about how a specific equipment provides a service.
    """

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='equipment_services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='equipment_services'
    )

    # Additional details specific to this equipment-service combination
    notes = models.TextField(
        blank=True,
        help_text="Specific notes about how this equipment provides this service"
    )

    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated cost in PLN (if different from general pricing)"
    )

    is_primary = models.BooleanField(
        default=False,
        help_text="Is this equipment primarily used for this service?"
    )

    is_available = models.BooleanField(
        default=True,
        help_text="Is this service currently available with this equipment?"
    )

    # Capacity and limitations
    capacity_per_day = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of samples/runs possible per day"
    )

    specific_limitations = models.TextField(
        blank=True,
        help_text="Specific limitations for this equipment-service combination"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', 'id']
        unique_together = [['equipment', 'service']]
        verbose_name = "Equipment-Service Link"
        verbose_name_plural = "Equipment-Service Links"

    def __str__(self):
        return f"{self.equipment.name} → {self.service.name}"

    @property
    def infrastructure(self):
        """Convenience property to get infrastructure."""
        return self.equipment.infrastructure

    @property
    def full_location(self):
        """Get full location string."""
        return self.equipment.full_location


# Add convenience property to Equipment model
def get_services(self):
    """Get all services offered by this equipment."""
    return Service.objects.filter(equipment_services__equipment=self)


Equipment.add_to_class('services', property(get_services))