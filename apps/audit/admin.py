from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, ChangeHistory, DataQualityMetric

from ScientaGrid.admin import admin_site


@admin.register(AuditLog, site=admin_site)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'user',
        'action_type',
        'object_repr',
        'category',
        'ip_address'
    ]
    list_filter = [
        'action_type',
        'category',
        'timestamp',
        'user'
    ]
    search_fields = [
        'object_repr',
        'description',
        'user__username',
        'ip_address'
    ]
    readonly_fields = [
        'user',
        'timestamp',
        'action_type',
        'content_type',
        'object_id',
        'object_repr',
        'description',
        'changes',
        'ip_address',
        'user_agent',
        'category'
    ]

    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Action Information', {
            'fields': ('timestamp', 'user', 'action_type', 'category')
        }),
        ('Object Information', {
            'fields': ('content_type', 'object_id', 'object_repr', 'description')
        }),
        ('Changes', {
            'fields': ('changes',),
            'classes': ('collapse',)
        }),
        ('Context', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs (keep for compliance)."""
        return False


@admin.register(ChangeHistory, site=admin_site)
class ChangeHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'content_type',
        'object_id',
        'field_name',
        'change_type',
        'user',
        'value_preview'
    ]
    list_filter = [
        'change_type',
        'content_type',
        'timestamp',
        'user'
    ]
    search_fields = [
        'field_name',
        'old_value',
        'new_value',
        'user__username'
    ]
    readonly_fields = [
        'timestamp',
        'user',
        'content_type',
        'object_id',
        'field_name',
        'old_value',
        'new_value',
        'change_type'
    ]

    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Change Information', {
            'fields': ('timestamp', 'user', 'change_type')
        }),
        ('Object', {
            'fields': ('content_type', 'object_id')
        }),
        ('Field Change', {
            'fields': ('field_name', 'old_value', 'new_value')
        }),
    )

    def value_preview(self, obj):
        """Show a preview of the change."""
        old = obj.old_value[:50] + '...' if len(obj.old_value) > 50 else obj.old_value
        new = obj.new_value[:50] + '...' if len(obj.new_value) > 50 else obj.new_value
        return format_html(
            '<span style="color: #888;">{}</span> → <span style="color: #0a0;">{}</span>',
            old, new
        )

    value_preview.short_description = 'Change'

    def has_add_permission(self, request):
        """Prevent manual creation."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion."""
        return False


@admin.register(DataQualityMetric, site=admin_site)
class DataQualityMetricAdmin(admin.ModelAdmin):
    list_display = [
        'content_type',
        'object_id',
        'quality_badge',
        'completeness_badge',
        'quality_level',  # This is OK in list_display
        'last_updated'
    ]
    list_filter = [
        'content_type',
        'has_description',
        'has_contact',
        'has_location',
        'has_documentation',
        'last_updated'
    ]
    search_fields = [
        'object_id'
    ]
    readonly_fields = [
        'content_type',
        'object_id',
        'completeness_score',
        'quality_score',
        'quality_level',  # Add as readonly to display in detail view
        'missing_fields',
        'warnings',
        'has_description',
        'has_contact',
        'has_location',
        'has_documentation',
        'has_pricing',
        'has_access_conditions',
        'calculated_at',
        'last_updated'
    ]

    fieldsets = (
        ('Object', {
            'fields': ('content_type', 'object_id')
        }),
        ('Scores', {
            'fields': ('quality_score', 'completeness_score', 'quality_level')  # Now in readonly_fields
        }),
        ('Completeness Checks', {
            'fields': (
                'has_description',
                'has_contact',
                'has_location',
                'has_documentation',
                'has_pricing',
                'has_access_conditions'
            )
        }),
        ('Issues', {
            'fields': ('missing_fields', 'warnings')
        }),
        ('Timestamps', {
            'fields': ('calculated_at', 'last_updated')
        }),
    )

    def quality_badge(self, obj):
        """Display quality score with color."""
        score = float(obj.quality_score)
        color = '#28a745' if score >= 75 else '#ffc107' if score >= 50 else '#dc3545'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}%</span>',
            color, f'{score:.1f}'
        )

    quality_badge.short_description = 'Quality Score'

    def completeness_badge(self, obj):
        """Display completeness score with color."""
        score = float(obj.completeness_score)
        color = '#28a745' if score >= 75 else '#ffc107' if score >= 50 else '#dc3545'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}%</span>',
            color, f'{score:.1f}'
        )

    completeness_badge.short_description = 'Completeness'

    # Actions
    actions = ['recalculate_metrics']

    def recalculate_metrics(self, request, queryset):
        """Recalculate quality metrics for selected objects."""
        count = 0
        for metric in queryset:
            try:
                obj = metric.content_object
                if obj:
                    DataQualityMetric.calculate_for_object(obj)
                    count += 1
            except Exception as e:
                self.message_user(request, f'Error recalculating for {metric}: {e}', level='error')

        self.message_user(request, f'Recalculated metrics for {count} objects.')

    recalculate_metrics.short_description = "Recalculate quality metrics"

    def has_delete_permission(self, request, obj=None):
        """Allow deletion to force recalculation."""
        return True