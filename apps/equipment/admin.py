from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(TranslatableAdmin):
    list_display = [
        'name',
        'infrastructure',
        'manufacturer',
        'model_number',
        'status',
        'is_available',
        'condition',
        'created_at'
    ]
    list_filter = [
        'status',
        'is_available',
        'condition',
        'requires_training',
        'infrastructure__institution',
        'infrastructure__city__region__country',
        'infrastructure__city__region',
        'created_at'
    ]
    filter_horizontal = ['technology_domains', 'tags']
    search_fields = [
        'translations__name',
        'translations__description',
        'manufacturer',
        'model_number',
        'serial_number',
        'infrastructure__translations__name'
    ]
    autocomplete_fields = ['infrastructure']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'infrastructure')
        }),
        ('Technical Information', {
            'fields': (
                'manufacturer',
                'model_number',
                'serial_number',
                'year_of_purchase',
                'technical_details',
                'sample_requirements'
            )
        }),
        ('Status & Availability', {
            'fields': ('status', 'is_available', 'condition', 'requires_training')
        }),
        ('Internal Notes', {
            'fields': ('internal_notes',),
            'classes': ('collapse',)
        }),
        ('Classification', {
            'fields': ('technology_domains', 'tags'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Add metadata fields when editing existing equipment."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Editing existing object
            return fieldsets + (
                ('Metadata', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    # Add action to mark equipment as available/unavailable
    actions = ['mark_available', 'mark_unavailable', 'mark_operational', 'mark_maintenance']

    def mark_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} equipment marked as available.')

    mark_available.short_description = "Mark selected as available"

    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} equipment marked as unavailable.')

    mark_unavailable.short_description = "Mark selected as unavailable"

    def mark_operational(self, request, queryset):
        updated = queryset.update(status='operational', is_available=True)
        self.message_user(request, f'{updated} equipment marked as operational.')

    mark_operational.short_description = "Mark selected as operational"

    def mark_maintenance(self, request, queryset):
        updated = queryset.update(status='maintenance', is_available=False)
        self.message_user(request, f'{updated} equipment marked as under maintenance.')

    mark_maintenance.short_description = "Mark selected as under maintenance"