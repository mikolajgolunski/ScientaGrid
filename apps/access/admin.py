from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import AccessCondition, PricingPolicy


@admin.register(AccessCondition)
class AccessConditionAdmin(TranslatableAdmin):
    list_display = [
        'name',
        'access_type',
        'get_applies_to',
        'requires_booking',
        'requires_training',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'access_type',
        'requires_booking',
        'requires_training',
        'requires_safety_certification',
        'requires_nda',
        'is_active',
        'created_at'
    ]
    search_fields = [
        'translations__name',
        'translations__description',
        'infrastructure__translations__name',
        'equipment__translations__name',
        'service__translations__name'
    ]
    autocomplete_fields = ['infrastructure', 'equipment', 'service']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'access_type')
        }),
        ('Applies To', {
            'fields': ('infrastructure', 'equipment', 'service'),
            'description': 'Select at least one: infrastructure, equipment, or service'
        }),
        ('Eligibility & Process', {
            'fields': (
                'eligibility_criteria',
                'application_process',
                'required_documents',
                'terms_and_conditions'
            )
        }),
        ('Booking Requirements', {
            'fields': (
                'requires_booking',
                'min_booking_days',
                'max_booking_days'
            )
        }),
        ('Training & Certifications', {
            'fields': (
                'requires_training',
                'training_duration_hours',
                'requires_safety_certification',
                'requires_nda',
                'requires_insurance'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Add metadata fields when editing existing access condition."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            return fieldsets + (
                ('Metadata', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    def get_applies_to(self, obj):
        """Show what this access condition applies to."""
        if obj.infrastructure:
            return f"Infrastructure: {obj.infrastructure.name}"
        elif obj.equipment:
            return f"Equipment: {obj.equipment.name}"
        elif obj.service:
            return f"Service: {obj.service.name}"
        return "Not specified"

    get_applies_to.short_description = 'Applies To'


@admin.register(PricingPolicy)
class PricingPolicyAdmin(TranslatableAdmin):
    list_display = [
        'name',
        'pricing_type',
        'base_price',
        'academic_price',
        'commercial_price',
        'get_applies_to',
        'is_active',
        'valid_from',
        'valid_until'
    ]
    list_filter = [
        'pricing_type',
        'is_active',
        'includes_operator',
        'includes_analysis',
        'valid_from',
        'created_at'
    ]
    search_fields = [
        'translations__name',
        'translations__description',
        'infrastructure__translations__name',
        'equipment__translations__name',
        'service__translations__name'
    ]
    autocomplete_fields = ['infrastructure', 'equipment', 'service']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'pricing_type')
        }),
        ('Applies To', {
            'fields': ('infrastructure', 'equipment', 'service'),
            'description': 'Select at least one: infrastructure, equipment, or service'
        }),
        ('Pricing (PLN)', {
            'fields': (
                'base_price',
                'academic_price',
                'commercial_price',
                'internal_price',
                'setup_fee'
            )
        }),
        ('Inclusions', {
            'fields': ('includes_operator', 'includes_analysis', 'price_notes')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Add metadata fields when editing existing pricing policy."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            return fieldsets + (
                ('Metadata', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    def get_applies_to(self, obj):
        """Show what this pricing policy applies to."""
        if obj.infrastructure:
            return f"Infrastructure: {obj.infrastructure.name}"
        elif obj.equipment:
            return f"Equipment: {obj.equipment.name}"
        elif obj.service:
            return f"Service: {obj.service.name}"
        return "Not specified"

    get_applies_to.short_description = 'Applies To'

    # Actions
    actions = ['mark_active', 'mark_inactive']

    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} pricing policies marked as active.')

    mark_active.short_description = "Mark selected as active"

    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} pricing policies marked as inactive.')

    mark_inactive.short_description = "Mark selected as inactive"