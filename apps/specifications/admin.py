from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Specification, SpecificationValue


@admin.register(Specification)
class SpecificationAdmin(TranslatableAdmin):
    list_display = [
        'code',
        'name',
        'data_type',
        'unit',
        'category',
        'display_order',
        'is_filterable',
        'is_active',
        'value_count'
    ]
    list_filter = [
        'data_type',
        'category',
        'is_filterable',
        'is_active',
        'created_at'
    ]
    search_fields = [
        'code',
        'translations__name',
        'translations__description'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'category')
        }),
        ('Data Type & Values', {
            'fields': ('data_type', 'unit', 'unit_label', 'choices')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_filterable')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Add metadata fields when editing."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            return fieldsets + (
                ('Metadata', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    def value_count(self, obj):
        """Count equipment using this specification."""
        return obj.values.count()

    value_count.short_description = 'Equipment Count'


class SpecificationValueInline(admin.TabularInline):
    """Inline admin for specification values."""
    model = SpecificationValue
    extra = 1
    fields = [
        'specification',
        'numeric_value',
        'range_min',
        'range_max',
        'text_value',
        'boolean_value',
        'choice_value',
        'is_verified'
    ]
    autocomplete_fields = ['specification']


@admin.register(SpecificationValue)
class SpecificationValueAdmin(admin.ModelAdmin):
    list_display = [
        'equipment',
        'specification',
        'get_display_value',
        'is_verified',
        'created_at'
    ]
    list_filter = [
        'specification__category',
        'specification',
        'is_verified',
        'created_at'
    ]
    search_fields = [
        'equipment__translations__name',
        'specification__translations__name',
        'text_value',
        'choice_value'
    ]
    autocomplete_fields = ['equipment', 'specification']

    fieldsets = (
        ('Basic Information', {
            'fields': ('equipment', 'specification')
        }),
        ('Values', {
            'fields': (
                'numeric_value',
                'range_min',
                'range_max',
                'text_value',
                'boolean_value',
                'choice_value'
            ),
            'description': 'Fill in the appropriate field based on the specification data type'
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_verified')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Add metadata fields when editing."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            return fieldsets + (
                ('Metadata', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    def get_display_value(self, obj):
        """Display the formatted value."""
        return obj.get_display_value()

    get_display_value.short_description = 'Value'

    # Actions
    actions = ['mark_verified', 'mark_unverified']

    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} specification values marked as verified.')

    mark_verified.short_description = "Mark selected as verified"

    def mark_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} specification values marked as unverified.')

    mark_unverified.short_description = "Mark selected as unverified"


# Update Equipment admin to include specifications inline
from apps.equipment.admin import EquipmentAdmin
from apps.equipment.models import Equipment

# Unregister and re-register with inline
admin.site.unregister(Equipment)


@admin.register(Equipment)
class EquipmentAdminWithSpecs(EquipmentAdmin):
    inlines = EquipmentAdmin.inlines if hasattr(EquipmentAdmin, 'inlines') else []
    inlines = list(inlines) + [SpecificationValueInline]