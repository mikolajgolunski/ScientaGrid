from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from .models import DocumentType, Document

from ScientaGrid.admin import admin_site


@admin.register(DocumentType, site=admin_site)
class DocumentTypeAdmin(TranslatableAdmin):
    list_display = [
        'code',
        'name',
        'allowed_extensions',
        'max_file_size_mb',
        'is_active',
        'document_count'
    ]
    list_filter = [
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
            'fields': ('code', 'name', 'description', 'icon')
        }),
        ('File Restrictions', {
            'fields': ('allowed_extensions', 'max_file_size_mb')
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

    def document_count(self, obj):
        """Count documents of this type."""
        return obj.documents.count()

    document_count.short_description = 'Documents'


class DocumentInline(TranslatableTabularInline):  # Changed from TabularInline to TranslatableTabularInline
    """Inline admin for documents."""
    model = Document
    extra = 1
    fields = ['title', 'file', 'document_type', 'status', 'is_public']
    autocomplete_fields = ['document_type']


@admin.register(Document, site=admin_site)
class DocumentAdmin(TranslatableAdmin):
    list_display = [
        'get_title',  # Changed from 'title' to custom method
        'get_filename',  # Changed from 'filename'
        'document_type',
        'get_related_to',
        'file_size_display',
        'status',
        'is_public',
        'download_count',
        'created_at'
    ]
    list_filter = [
        'status',
        'is_public',
        'requires_login',
        'document_type',
        'file_extension',
        'created_at'
    ]
    search_fields = [
        'translations__title',
        'translations__description',
        'file',
        'infrastructure__translations__name',
        'equipment__translations__name',
        'service__translations__name'
    ]
    autocomplete_fields = [
        'infrastructure',
        'equipment',
        'service',
        'document_type',
        'uploaded_by',
        'replaces'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'document_type')
        }),
        ('File', {
            'fields': ('file', 'version', 'replaces')
        }),
        ('Related To', {
            'fields': ('infrastructure', 'equipment', 'service'),
            'description': 'Select at least one: infrastructure, equipment, or service'
        }),
        ('Access Control', {
            'fields': ('status', 'is_public', 'requires_login')
        }),
    )

    readonly_fields = [
        'file_size',
        'file_extension',
        'mime_type',
        'download_count',
        'last_downloaded_at',
        'uploaded_by',
        'created_at',
        'updated_at'
    ]

    def get_title(self, obj):
        """Display title using safe_translation_getter."""
        return obj.safe_translation_getter('title', any_language=True) or obj.filename
    get_title.short_description = 'Title'
    get_title.admin_order_field = 'translations__title'

    def get_filename(self, obj):
        """Display filename with download link."""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                obj.file.url,
                obj.filename
            )
        return "-"
    get_filename.short_description = 'File'

    def get_queryset(self, request):
        """Override to get distinct documents."""
        qs = Document.objects.all()
        ordering = self.get_ordering(request) or ['-created_at']
        safe_ordering = [o for o in ordering if 'translation' not in o]
        if safe_ordering:
            qs = qs.order_by(*safe_ordering)
        return qs

    def get_fieldsets(self, request, obj=None):
        """Add metadata fields when editing."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            return fieldsets + (
                ('File Metadata', {
                    'fields': (
                        'file_size',
                        'file_extension',
                        'mime_type'
                    ),
                    'classes': ('collapse',)
                }),
                ('Statistics', {
                    'fields': (
                        'download_count',
                        'last_downloaded_at'
                    ),
                    'classes': ('collapse',)
                }),
                ('Metadata', {
                    'fields': ('uploaded_by', 'created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        """Automatically set uploaded_by to current user."""
        if not change:  # Only set on creation
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    def get_related_to(self, obj):
        """Show what this document is related to."""
        related = obj.get_related_object()
        if related:
            return f"{related.__class__.__name__}: {related}"
        return "Not specified"

    get_related_to.short_description = 'Related To'

    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        if obj.file_size:
            if obj.file_size_mb >= 1:
                return f"{obj.file_size_mb} MB"
            else:
                return f"{round(obj.file_size / 1024, 2)} KB"
        return "-"

    file_size_display.short_description = 'File Size'

    # Actions
    actions = [
        'mark_active',
        'mark_archived',
        'mark_public',
        'mark_private'
    ]

    def mark_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} documents marked as active.')

    mark_active.short_description = "Mark selected as active"

    def mark_archived(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} documents marked as archived.')

    mark_archived.short_description = "Mark selected as archived"

    def mark_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} documents marked as public.')

    mark_public.short_description = "Mark selected as public"

    def mark_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} documents marked as private.')

    mark_private.short_description = "Mark selected as private"


# Update other admins to include document inline
from apps.infrastructures.admin import InfrastructureAdmin
from apps.infrastructures.models import Infrastructure
from apps.equipment.admin import EquipmentAdmin
from apps.equipment.models import Equipment
from apps.services.admin import ServiceAdmin
from apps.services.models import Service

# Unregister and re-register with document inline

# Infrastructure
admin_site.unregister(Infrastructure)


@admin.register(Infrastructure, site=admin_site)
class InfrastructureAdminWithDocs(InfrastructureAdmin):
    inlines = list(InfrastructureAdmin.inlines) if hasattr(InfrastructureAdmin, 'inlines') else []
    inlines = inlines + [DocumentInline]


# Equipment (already has SpecificationValueInline)
admin_site.unregister(Equipment)


@admin.register(Equipment, site=admin_site)
class EquipmentAdminWithDocs(EquipmentAdmin):
    # Get existing inlines if any
    existing_inlines = []
    if hasattr(EquipmentAdmin, 'inlines'):
        existing_inlines = list(EquipmentAdmin.inlines)
    inlines = existing_inlines + [DocumentInline]


# Service
admin_site.unregister(Service)


@admin.register(Service, site=admin_site)
class ServiceAdminWithDocs(ServiceAdmin):
    inlines = list(ServiceAdmin.inlines) if hasattr(ServiceAdmin, 'inlines') else []
    inlines = inlines + [DocumentInline]