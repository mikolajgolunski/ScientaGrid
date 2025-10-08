from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment
from apps.services.models import Service


class AccessCondition(TranslatableModel):
    """Defines access policies and conditions for infrastructures, equipment, or services."""

    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True),
        eligibility_criteria=models.TextField(
            blank=True,
            help_text="Who is eligible to access (e.g., academic researchers, companies)"
        ),
        application_process=models.TextField(
            blank=True,
            help_text="How to apply for access"
        ),
        required_documents=models.TextField(
            blank=True,
            help_text="Documents required for access application"
        ),
        terms_and_conditions=models.TextField(
            blank=True,
            help_text="Terms and conditions of use"
        )
    )

    # What this access condition applies to
    infrastructure = models.ForeignKey(
        Infrastructure,
        on_delete=models.CASCADE,
        related_name='access_conditions',
        null=True,
        blank=True,
        help_text="Leave blank if this applies to specific equipment/services"
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='access_conditions',
        null=True,
        blank=True
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='access_conditions',
        null=True,
        blank=True
    )

    # Access types
    ACCESS_TYPES = [
        ('open', 'Open Access'),
        ('restricted', 'Restricted Access'),
        ('by_approval', 'By Approval'),
        ('commercial', 'Commercial Only'),
        ('academic', 'Academic Only'),
        ('collaborative', 'Collaborative Projects Only'),
    ]
    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPES,
        default='by_approval'
    )

    # Time constraints
    requires_booking = models.BooleanField(
        default=True,
        help_text="Does access require advance booking?"
    )
    min_booking_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minimum days in advance for booking"
    )
    max_booking_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum days in advance for booking"
    )

    # Training requirements
    requires_training = models.BooleanField(
        default=False,
        help_text="Is training required before access?"
    )
    training_duration_hours = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duration of required training in hours"
    )

    # Other requirements
    requires_safety_certification = models.BooleanField(default=False)
    requires_nda = models.BooleanField(
        default=False,
        help_text="Non-disclosure agreement required?"
    )
    requires_insurance = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or f"Access Condition {self.id}"
        if self.infrastructure:
            return f"{name} ({self.infrastructure.name})"
        elif self.equipment:
            return f"{name} ({self.equipment.name})"
        elif self.service:
            return f"{name} ({self.service.name})"
        return name

    def clean(self):
        """Ensure at least one of infrastructure, equipment, or service is set."""
        from django.core.exceptions import ValidationError
        if not any([self.infrastructure, self.equipment, self.service]):
            raise ValidationError(
                'Access condition must be linked to at least one: infrastructure, equipment, or service'
            )


class PricingPolicy(TranslatableModel):
    """Defines pricing for accessing infrastructures, equipment, or services."""

    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True),
        price_notes=models.TextField(
            blank=True,
            help_text="Additional notes about pricing (discounts, special conditions, etc.)"
        )
    )

    # What this pricing applies to
    infrastructure = models.ForeignKey(
        Infrastructure,
        on_delete=models.CASCADE,
        related_name='pricing_policies',
        null=True,
        blank=True
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='pricing_policies',
        null=True,
        blank=True
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='pricing_policies',
        null=True,
        blank=True
    )

    # Pricing structure
    PRICING_TYPES = [
        ('free', 'Free'),
        ('per_hour', 'Per Hour'),
        ('per_day', 'Per Day'),
        ('per_sample', 'Per Sample'),
        ('per_measurement', 'Per Measurement'),
        ('per_project', 'Per Project'),
        ('custom', 'Custom Quote'),
    ]
    pricing_type = models.CharField(
        max_length=20,
        choices=PRICING_TYPES,
        default='per_hour'
    )

    # Price in PLN
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Base price in PLN"
    )

    # Different rates for different user types
    academic_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Discounted price for academic users in PLN"
    )
    commercial_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price for commercial users in PLN"
    )
    internal_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price for internal institutional users in PLN"
    )

    # Additional costs
    setup_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="One-time setup fee in PLN"
    )

    includes_operator = models.BooleanField(
        default=False,
        help_text="Does the price include operator/technical support?"
    )
    includes_analysis = models.BooleanField(
        default=False,
        help_text="Does the price include data analysis?"
    )

    # Validity
    valid_from = models.DateField(
        null=True,
        blank=True,
        help_text="Date from which this pricing is valid"
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        help_text="Date until which this pricing is valid"
    )

    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-valid_from', 'id']
        verbose_name_plural = "Pricing Policies"

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or f"Pricing {self.id}"
        if self.base_price:
            return f"{name} ({self.base_price} PLN)"
        return name

    def clean(self):
        """Ensure at least one of infrastructure, equipment, or service is set."""
        from django.core.exceptions import ValidationError
        if not any([self.infrastructure, self.equipment, self.service]):
            raise ValidationError(
                'Pricing policy must be linked to at least one: infrastructure, equipment, or service'
            )