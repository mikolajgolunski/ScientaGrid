from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Infrastructure, ContactPerson


class ContactPersonInline(admin.TabularInline):
    """Inline admin for contact persons."""
    model = ContactPerson
    extra = 1
    fields = ['first_name', 'last_name', 'position', 'email', 'phone', 'is_primary']


@admin.register(Infrastructure)
class InfrastructureAdmin(TranslatableAdmin):
    list_display = [
        'name',
        'institution',
        'city',
        'reliability',
        'is_active',
        'is_verified',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'is_verified',
        'reliability',
        'city__region__country',
        'city__region',
        'institution__institution_type',
        'created_at'
    ]
    filter_horizontal = ['technology_domains', 'categories', 'tags']
    search_fields = [
        'translations__name',
        'translations__description',
        'institution__translations__name',
        'email',
        'website'
    ]
    autocomplete_fields = ['institution', 'city', 'created_by']

    inlines = [ContactPersonInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'institution', 'city')
        }),
        ('Contact Information', {
            'fields': ('website', 'email', 'phone')
        }),
        ('Status & Quality', {
            'fields': ('is_active', 'is_verified', 'reliability')
        }),
        ('Internal Notes', {
            'fields': ('internal_comments',),
            'classes': ('collapse',)
        }),
        ('Classification', {
            'fields': ('technology_domains', 'categories', 'tags'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_by', 'created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Add metadata fields when editing existing infrastructure."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Editing existing object
            return fieldsets + (
                ('Metadata', {
                    'fields': ('created_by', 'created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        """Automatically set created_by to current user."""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'position',
        'infrastructure',
        'email',
        'is_primary',
        'created_at'
    ]
    list_filter = ['is_primary', 'created_at']
    search_fields = [
        'first_name',
        'last_name',
        'email',
        'infrastructure__translations__name'
    ]
    autocomplete_fields = ['infrastructure']

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'position')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'is_primary')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']