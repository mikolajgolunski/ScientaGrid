from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Service, EquipmentService


class EquipmentServiceInline(admin.TabularInline):
    """Inline admin for equipment-service relationships."""
    model = EquipmentService
    extra = 1
    fields = [
        'equipment',
        'is_primary',
        'is_available',
        'estimated_cost',
        'capacity_per_day',
        'notes'
    ]
    autocomplete_fields = ['equipment']


@admin.register(Service)
class ServiceAdmin(TranslatableAdmin):
    list_display = [
        'name',
        'code',
        'typical_turnaround_days',
        'is_active',
        'equipment_count',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'typical_turnaround_days',
        'created_at'
    ]
    filter_horizontal = ['technology_domains', 'tags']
    search_fields = [
        'translations__name',
        'translations__description',
        'code'
    ]

    inlines = [EquipmentServiceInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Service Details', {
            'fields': (
                'methodology',
                'typical_applications',
                'deliverables',
                'typical_turnaround_days'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Classification', {
            'fields': ('technology_domains', 'tags'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Add metadata fields when editing existing service."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Editing existing object
            return fieldsets + (
                ('Metadata', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    def equipment_count(self, obj):
        """Show number of equipment offering this service."""
        return obj.equipment_services.count()

    equipment_count.short_description = 'Equipment Count'

    # Actions
    actions = ['mark_active', 'mark_inactive']

    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} services marked as active.')

    mark_active.short_description = "Mark selected as active"

    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} services marked as inactive.')

    mark_inactive.short_description = "Mark selected as inactive"


@admin.register(EquipmentService)
class EquipmentServiceAdmin(admin.ModelAdmin):
    list_display = [
        'service',
        'equipment',
        'infrastructure',
        'is_primary',
        'is_available',
        'estimated_cost',
        'capacity_per_day',
        'created_at'
    ]
    list_filter = [
        'is_primary',
        'is_available',
        'service',
        'equipment__infrastructure',
        'created_at'
    ]
    search_fields = [
        'service__translations__name',
        'equipment__translations__name',
        'equipment__infrastructure__translations__name'
    ]
    autocomplete_fields = ['equipment', 'service']

    fieldsets = (
        ('Relationship', {
            'fields': ('equipment', 'service')
        }),
        ('Service Characteristics', {
            'fields': (
                'is_primary',
                'is_available',
                'estimated_cost',
                'capacity_per_day'
            )
        }),
        ('Details', {
            'fields': ('notes', 'specific_limitations')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def infrastructure(self, obj):
        """Show infrastructure name."""
        return obj.equipment.infrastructure.name

    infrastructure.short_description = 'Infrastructure'

    # Actions
    actions = ['mark_available', 'mark_unavailable', 'mark_primary']

    def mark_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} equipment-service links marked as available.')

    mark_available.short_description = "Mark selected as available"

    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} equipment-service links marked as unavailable.')

    mark_unavailable.short_description = "Mark selected as unavailable"

    def mark_primary(self, request, queryset):
        updated = queryset.update(is_primary=True)
        self.message_user(request, f'{updated} equipment-service links marked as primary.')

    mark_primary.short_description = "Mark selected as primary"