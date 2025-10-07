from django.contrib import admin
from django.utils.html import format_html
from .models import SavedSearch, SearchLog
from .admin_views import register_search_admin_view

# Register custom search view
register_search_admin_view(admin.site)


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'user',
        'search_type',
        'usage_count',
        'last_used_at',
        'notify_on_new_results',
        'is_active',
        'created_at',
        'execute_search_link'
    ]
    list_filter = [
        'search_type',
        'is_active',
        'notify_on_new_results',
        'created_at',
        'last_used_at'
    ]
    search_fields = [
        'name',
        'description',
        'user__username'
    ]
    readonly_fields = ['usage_count', 'last_used_at', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'search_type')
        }),
        ('Search Parameters', {
            'fields': ('search_params',)
        }),
        ('Settings', {
            'fields': ('notify_on_new_results', 'is_active')
        }),
        ('Statistics', {
            'fields': ('usage_count', 'last_used_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def execute_search_link(self, obj):
        """Add link to execute this saved search."""
        # Build search URL based on search_params
        params = obj.get_params_dict()
        query = params.get('query_text', '')
        return format_html(
            '<a href="/admin/search/?q={}&type={}" target="_blank">Execute</a>',
            query,
            obj.search_type
        )

    execute_search_link.short_description = 'Execute'


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'user',
        'search_type',
        'query_preview',
        'results_count',
        'execution_time_display'
    ]
    list_filter = [
        'search_type',
        'timestamp'
    ]
    search_fields = [
        'query_text',
        'user__username',
        'session_id'
    ]
    readonly_fields = [
        'user',
        'timestamp',
        'query_text',
        'filters',
        'search_type',
        'results_count',
        'execution_time_ms',
        'clicked_result_ids',
        'session_id'
    ]

    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Search Information', {
            'fields': ('timestamp', 'user', 'search_type', 'session_id')
        }),
        ('Query', {
            'fields': ('query_text', 'filters')
        }),
        ('Results', {
            'fields': ('results_count', 'execution_time_ms', 'clicked_result_ids')
        }),
    )

    def query_preview(self, obj):
        """Show preview of query text."""
        if obj.query_text:
            preview = obj.query_text[:50]
            if len(obj.query_text) > 50:
                preview += '...'
            return preview
        return '-'

    query_preview.short_description = 'Query'

    def execution_time_display(self, obj):
        """Display execution time with color coding."""
        if obj.execution_time_ms is None:
            return '-'

        # Color code based on performance
        if obj.execution_time_ms < 100:
            color = '#28a745'  # Green
        elif obj.execution_time_ms < 500:
            color = '#ffc107'  # Yellow
        else:
            color = '#dc3545'  # Red

        return format_html(
            '<span style="color: {};">{} ms</span>',
            color, obj.execution_time_ms
        )

    execution_time_display.short_description = 'Execution Time'

    def has_add_permission(self, request):
        """Prevent manual creation."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make read-only."""
        return False