from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Institution


@admin.register(Institution)
class InstitutionAdmin(TranslatableAdmin):
    list_display = [
        'name',
        'institution_type',
        'city',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'institution_type',
        'is_active',
        'city__region__country',
        'city__region',
        'created_at'
    ]
    search_fields = [
        'translations__name',
        'translations__address',
        'email',
        'website'
    ]
    autocomplete_fields = ['city']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'institution_type', 'is_active')
        }),
        ('Location', {
            'fields': ('city', 'address')
        }),
        ('Contact Information', {
            'fields': ('website', 'email', 'phone')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Add timestamps to fieldsets when editing existing institution."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Editing existing object
            return fieldsets + (
                ('Metadata', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets