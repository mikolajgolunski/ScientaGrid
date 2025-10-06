from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import TechnologyDomain, InfrastructureCategory, Tag


@admin.register(TechnologyDomain)
class TechnologyDomainAdmin(TranslatableAdmin):
    list_display = [
        'code',
        'name',
        'parent',
        'level',
        'is_active',
        'infrastructure_count',
        'equipment_count',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'parent',
        'created_at'
    ]
    search_fields = [
        'code',
        'translations__name',
        'translations__description'
    ]
    autocomplete_fields = ['parent']

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent',)
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

    def level(self, obj):
        """Show hierarchy level."""
        return obj.level

    level.short_description = 'Level'

    def infrastructure_count(self, obj):
        """Count infrastructures using this domain."""
        return obj.infrastructures.count()

    infrastructure_count.short_description = 'Infrastructures'

    def equipment_count(self, obj):
        """Count equipment using this domain."""
        return obj.equipment.count()

    equipment_count.short_description = 'Equipment'


@admin.register(InfrastructureCategory)
class InfrastructureCategoryAdmin(TranslatableAdmin):
    list_display = [
        'code',
        'name',
        'technology_domain',
        'parent',
        'level',
        'is_active',
        'infrastructure_count',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'technology_domain',
        'parent',
        'created_at'
    ]
    search_fields = [
        'code',
        'translations__name',
        'translations__description'
    ]
    autocomplete_fields = ['parent', 'technology_domain']

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Classification', {
            'fields': ('technology_domain', 'parent')
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

    def level(self, obj):
        """Show hierarchy level."""
        return obj.level

    level.short_description = 'Level'

    def infrastructure_count(self, obj):
        """Count infrastructures in this category."""
        return obj.infrastructures.count()

    infrastructure_count.short_description = 'Infrastructures'


@admin.register(Tag)
class TagAdmin(TranslatableAdmin):
    list_display = [
        'name',
        'slug',
        'tag_type',
        'color_preview',
        'usage_count',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'tag_type',
        'is_active',
        'created_at'
    ]
    search_fields = [
        'translations__name',
        'slug',
        'translations__description'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'tag_type')
        }),
        ('Display', {
            'fields': ('color',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    readonly_fields = ['usage_count', 'created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Add metadata fields when editing."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            return fieldsets + (
                ('Statistics', {
                    'fields': ('usage_count',),
                    'classes': ('collapse',)
                }),
                ('Metadata', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    def color_preview(self, obj):
        """Show color preview."""
        if obj.color:
            return f'<span style="background-color: {obj.color}; padding: 5px 20px; border: 1px solid #ccc;">&nbsp;</span>'
        return '-'

    color_preview.short_description = 'Color'
    color_preview.allow_tags = True

    # Actions
    actions = ['reset_usage_count']

    def reset_usage_count(self, request, queryset):
        updated = queryset.update(usage_count=0)
        self.message_user(request, f'Reset usage count for {updated} tags.')

    reset_usage_count.short_description = "Reset usage count to 0"