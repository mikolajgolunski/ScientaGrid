from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from apps.locations.models import City


class Institution(TranslatableModel):
    """Represents an organization that hosts research infrastructures."""

    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True),
        address=models.CharField(max_length=255, blank=True)
    )

    # Non-translatable fields
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='institutions')
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    # Institution type choices
    INSTITUTION_TYPES = [
        ('university', 'University'),
        ('research_institute', 'Research Institute'),
        ('company', 'Company'),
        ('hospital', 'Hospital'),
        ('government', 'Government Agency'),
        ('ngo', 'Non-Governmental Organization'),
        ('other', 'Other'),
    ]
    institution_type = models.CharField(
        max_length=50,
        choices=INSTITUTION_TYPES,
        default='university'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or f"Institution {self.id}"

    @property
    def region(self):
        """Convenience property to get region through city."""
        return self.city.region

    @property
    def country(self):
        """Convenience property to get country through city."""
        return self.city.region.country