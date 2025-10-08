from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from apps.equipment.models import Equipment


class Specification(TranslatableModel):
    """Represents a technical specification type (e.g., resolution, temperature range)."""

    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        description=models.TextField(blank=True),
        unit_label=models.CharField(
            max_length=50,
            blank=True,
            help_text="Display label for the unit (e.g., 'nanometers', 'degrees Celsius')"
        )
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for this specification type"
    )

    # Data type for values
    DATA_TYPES = [
        ('numeric', 'Numeric'),
        ('range', 'Numeric Range'),
        ('text', 'Text'),
        ('boolean', 'Yes/No'),
        ('choice', 'Multiple Choice'),
    ]
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPES,
        default='numeric',
        help_text="Type of data this specification stores"
    )

    # Unit information (non-translatable)
    unit = models.CharField(
        max_length=20,
        blank=True,
        help_text="Standard unit symbol (e.g., 'nm', '°C', 'kV')"
    )

    # For choice-type specifications
    choices = models.TextField(
        blank=True,
        help_text="Comma-separated list of choices (for choice data type)"
    )

    # Categorization
    CATEGORIES = [
        ('dimensional', 'Dimensional/Size'),
        ('performance', 'Performance'),
        ('environmental', 'Environmental'),
        ('sample', 'Sample Requirements'),
        ('operational', 'Operational Parameters'),
        ('output', 'Output Specifications'),
        ('other', 'Other'),
    ]
    category = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        default='performance'
    )

    # Display settings
    display_order = models.IntegerField(
        default=0,
        help_text="Order for displaying specifications (lower = first)"
    )

    is_filterable = models.BooleanField(
        default=True,
        help_text="Can this specification be used for filtering equipment?"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'display_order', 'id']

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or f"Specification {self.id}"
        if self.unit:
            return f"{name} ({self.unit})"
        return name

    def get_choices_list(self):
        """Parse choices string into a list."""
        if self.choices:
            return [choice.strip() for choice in self.choices.split(',')]
        return []


class SpecificationValue(models.Model):
    """Stores actual specification values for equipment."""

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='specification_values'
    )
    specification = models.ForeignKey(
        Specification,
        on_delete=models.CASCADE,
        related_name='values'
    )

    # Different value fields for different data types
    numeric_value = models.DecimalField(
        max_digits=15,
        decimal_places=5,
        null=True,
        blank=True,
        help_text="For numeric data type"
    )

    range_min = models.DecimalField(
        max_digits=15,
        decimal_places=5,
        null=True,
        blank=True,
        help_text="Minimum value for range data type"
    )

    range_max = models.DecimalField(
        max_digits=15,
        decimal_places=5,
        null=True,
        blank=True,
        help_text="Maximum value for range data type"
    )

    text_value = models.TextField(
        blank=True,
        help_text="For text data type"
    )

    boolean_value = models.BooleanField(
        null=True,
        blank=True,
        help_text="For boolean data type"
    )

    choice_value = models.CharField(
        max_length=200,
        blank=True,
        help_text="For choice data type"
    )

    # Additional context
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this specification value"
    )

    # Verification
    is_verified = models.BooleanField(
        default=False,
        help_text="Has this value been verified by staff?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['specification__category', 'specification__display_order']
        unique_together = [['equipment', 'specification']]
        verbose_name = "Specification Value"
        verbose_name_plural = "Specification Values"

    def __str__(self):
        return f"{self.equipment.name} - {self.specification.name}: {self.get_display_value()}"

    def get_display_value(self):
        """Return the appropriate value based on specification data type."""
        if self.specification.data_type == 'numeric' and self.numeric_value is not None:
            if self.specification.unit:
                return f"{self.numeric_value} {self.specification.unit}"
            return str(self.numeric_value)

        elif self.specification.data_type == 'range':
            if self.range_min is not None and self.range_max is not None:
                if self.specification.unit:
                    return f"{self.range_min}-{self.range_max} {self.specification.unit}"
                return f"{self.range_min}-{self.range_max}"
            elif self.range_min is not None:
                if self.specification.unit:
                    return f"≥ {self.range_min} {self.specification.unit}"
                return f"≥ {self.range_min}"
            elif self.range_max is not None:
                if self.specification.unit:
                    return f"≤ {self.range_max} {self.specification.unit}"
                return f"≤ {self.range_max}"

        elif self.specification.data_type == 'text':
            return self.text_value

        elif self.specification.data_type == 'boolean':
            if self.boolean_value is not None:
                return "Yes" if self.boolean_value else "No"

        elif self.specification.data_type == 'choice':
            return self.choice_value

        return "Not set"

    def clean(self):
        """Validate that the correct value field is used for the specification data type."""
        from django.core.exceptions import ValidationError

        if self.specification.data_type == 'numeric' and self.numeric_value is None:
            raise ValidationError("Numeric value is required for numeric specifications")

        elif self.specification.data_type == 'range':
            if self.range_min is None and self.range_max is None:
                raise ValidationError("At least one range value (min or max) is required")

        elif self.specification.data_type == 'text' and not self.text_value:
            raise ValidationError("Text value is required for text specifications")

        elif self.specification.data_type == 'boolean' and self.boolean_value is None:
            raise ValidationError("Boolean value is required for boolean specifications")

        elif self.specification.data_type == 'choice' and not self.choice_value:
            raise ValidationError("Choice value is required for choice specifications")