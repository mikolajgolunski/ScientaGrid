from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from .services import SearchService


class SearchAdminView:
    """Custom admin view for searching."""

    def get_urls(self):
        """Add custom URL for search view."""
        urls = [
            path('search/', self.admin_site.admin_view(self.search_view), name='search_interface'),
        ]
        return urls

    def search_view(self, request):
        """Handle search requests."""
        context = {
            'title': 'Search',
            'opts': {'app_label': 'search'},
        }

        if request.method == 'GET' and request.GET.get('q'):
            query = request.GET.get('q')
            search_type = request.GET.get('type', 'unified')

            if search_type == 'unified':
                results = SearchService.unified_search(query)
                context['results'] = results
            elif search_type == 'infrastructure':
                infra_results, time_ms, count = SearchService.search_infrastructures(query)
                context['infrastructures'] = infra_results[:50]
                context['count'] = count
                context['time_ms'] = time_ms
            elif search_type == 'equipment':
                equip_results, time_ms, count = SearchService.search_equipment(query)
                context['equipment'] = equip_results[:50]
                context['count'] = count
                context['time_ms'] = time_ms
            elif search_type == 'service':
                svc_results, time_ms, count = SearchService.search_services(query)
                context['services'] = svc_results[:50]
                context['count'] = count
                context['time_ms'] = time_ms

            context['query'] = query
            context['search_type'] = search_type

        return render(request, 'admin/search/search_interface.html', context)


# Register the view
def register_search_admin_view(admin_site):
    """Register custom search view with admin."""
    search_view = SearchAdminView()
    search_view.admin_site = admin_site

    # Add to admin URLs
    original_get_urls = admin_site.get_urls

    def get_urls():
        urls = original_get_urls()
        custom_urls = search_view.get_urls()
        return custom_urls + urls

    admin_site.get_urls = get_urls