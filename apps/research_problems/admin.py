from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import FieldOfScience, Keyword, ResearchProblem


@admin.register(FieldOfScience)
class FieldOfScienceAdmin(TranslatableAdmin):
    list_display = [
        'code',
        'name',
        'parent',
        'level',
        'is_active',
        'problem_count',
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

    def problem_count(self, obj):
        """Count research problems in this field."""
        return obj.research_problems.count()

    problem_count.short_description = 'Research Problems'


@admin.register(Keyword)
class KeywordAdmin(TranslatableAdmin):
    list_display = [
        'name',
        'slug',
        'field_of_science',
        'usage_count',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'field_of_science',
        'created_at'
    ]
    search_fields = [
        'translations__name',
        'slug',
        'translations__description'
    ]
    autocomplete_fields = ['field_of_science']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'field_of_science')
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

    # Actions
    actions = ['reset_usage_count']

    def reset_usage_count(self, request, queryset):
        updated = queryset.update(usage_count=0)
        self.message_user(request, f'Reset usage count for {updated} keywords.')

    reset_usage_count.short_description = "Reset usage count to 0"


@admin.register(ResearchProblem)
class ResearchProblemAdmin(TranslatableAdmin):
    list_display = [
        'title',
        'field_of_science',
        'status',
        'priority',
        'complexity',
        'submitted_by',
        'is_public',
        'created_at'
    ]
    list_filter = [
        'status',
        'priority',
        'complexity',
        'is_public',
        'field_of_science',
        'created_at'
    ]
    search_fields = [
        'translations__title',
        'translations__description',
        'submitted_by',
        'contact_email'
    ]
    autocomplete_fields = ['field_of_science']
    filter_horizontal = ['additional_fields', 'keywords']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'is_public')
        }),
        ('Classification', {
            'fields': ('field_of_science', 'additional_fields', 'keywords')
        }),
        ('Problem Details', {
            'fields': (
                'required_capabilities',
                'expected_outcomes',
                'constraints',
                'complexity',
                'priority'
            )
        }),
        ('Budget & Timeline', {
            'fields': ('estimated_budget', 'estimated_duration_days')
        }),
        ('Contact Information', {
            'fields': ('submitted_by', 'contact_email')
        }),
        ('Internal Notes', {
            'fields': ('internal_notes',),
            'classes': ('collapse',)
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

    # Actions
    actions = [
        'mark_active',
        'mark_matched',
        'mark_completed',
        'mark_public',
        'mark_private'
    ]

    def mark_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} research problems marked as active.')

    mark_active.short_description = "Mark selected as active"

    def mark_matched(self, request, queryset):
        updated = queryset.update(status='matched')
        self.message_user(request, f'{updated} research problems marked as matched.')

    mark_matched.short_description = "Mark selected as matched"

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} research problems marked as completed.')

    mark_completed.short_description = "Mark selected as completed"

    def mark_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} research problems marked as public.')

    mark_public.short_description = "Mark selected as public"

    def mark_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} research problems marked as private.')

    mark_private.short_description = "Mark selected as private"