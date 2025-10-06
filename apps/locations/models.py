from parler.models import TranslatableModel, TranslatedFields

from django.db import models


class Country(TranslatableModel):
    """Represents a country."""

    translations = TranslatedFields(
        name=models.CharField(max_length=100)
    )
    code = models.CharField(max_length=2, unique=True, help_text="ISO 3166-1 alpha-2 code")

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ["code"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or self.code


class Region(TranslatableModel):
    """Represents a region."""

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="regions")
    translations = TranslatedFields(
        name=models.CharField(max_length=100)
    )
    code = models.CharField(max_length=10, help_text="Region code")

    class Meta:
        ordering = ["country", "code"]
        unique_together = [["country", "code"]]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or self.code


class City(TranslatableModel):
    """Represents a city."""

    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="cities")
    translations = TranslatedFields(
        name=models.CharField(max_length=100)
    )
    postal_code = models.CharField(max_length=20, blank=True, help_text="Postal code")

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ["region", "translations__name"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or f"City {self.id}"

    @property
    def country(self):
        """Convenience property to get the country of the city."""
        return self.region.country