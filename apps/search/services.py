from django.db.models import Q, Count, Prefetch
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment
from apps.services.models import Service, EquipmentService
from apps.research_problems.models import ResearchProblem
from apps.specifications.models import SpecificationValue
import time


class SearchService:
    """Main search service for querying the database."""

    @staticmethod
    def _deduplicate_queryset(queryset):
        """
        Deduplicate queryset results by ID.
        Needed because django-parler with MySQL can create duplicates.
        """
        seen_ids = set()
        unique_results = []
        for obj in queryset:
            if obj.id not in seen_ids:
                seen_ids.add(obj.id)
                unique_results.append(obj)
        return unique_results

    @staticmethod
    def search_infrastructures(query_text=None, filters=None, apply_ranking=True):
        """
        Search infrastructures with filters.

        Args:
            query_text: Free text search query
            filters: Dictionary of filter parameters
                - city_id: Filter by city
                - region_id: Filter by region
                - country_id: Filter by country
                - institution_id: Filter by institution
                - is_active: Filter active/inactive
                - is_verified: Filter verified
                - technology_domains: List of domain IDs
                - categories: List of category IDs
                - tags: List of tag IDs
                - min_reliability: Minimum reliability score
                - access_type: Filter by access type (open, restricted, etc.)
                - has_pricing: Filter infrastructures with pricing
                - max_price: Maximum price filter
            apply_ranking: Whether to apply ranking to results (default: True)

            Returns:
                Tuple of (results_list, execution_time_ms, total_count)
        """
        start_time = time.time()
        queryset = Infrastructure.objects.select_related(
            'institution',
            'city',
            'city__region',
            'city__region__country'
        ).prefetch_related(
            'technology_domains',
            'categories',
            'tags',
            'contact_persons',
            'equipment',
            'access_conditions',
            'pricing_policies'
        )

        filters = filters or {}

        # Text search
        if query_text:
            queryset = queryset.filter(
                Q(translations__name__icontains=query_text) |
                Q(translations__description__icontains=query_text) |
                Q(institution__translations__name__icontains=query_text) |
                Q(translations__internal_comments__icontains=query_text) |
                Q(city__translations__name__icontains=query_text) |
                Q(city__region__translations__name__icontains=query_text)
            )

        # Location filters
        if filters.get('city_id'):
            queryset = queryset.filter(city_id=filters['city_id'])
        if filters.get('region_id'):
            queryset = queryset.filter(city__region_id=filters['region_id'])
        if filters.get('country_id'):
            queryset = queryset.filter(city__region__country_id=filters['country_id'])

        # Institution filter
        if filters.get('institution_id'):
            queryset = queryset.filter(institution_id=filters['institution_id'])

        # Status filters
        if 'is_active' in filters:
            queryset = queryset.filter(is_active=filters['is_active'])
        if 'is_verified' in filters:
            queryset = queryset.filter(is_verified=filters['is_verified'])

        # Reliability filter
        if filters.get('min_reliability'):
            queryset = queryset.filter(reliability__gte=filters['min_reliability'])

        # Technology domains
        if filters.get('technology_domains'):
            queryset = queryset.filter(technology_domains__id__in=filters['technology_domains'])

        # Categories
        if filters.get('categories'):
            queryset = queryset.filter(categories__id__in=filters['categories'])

        # Tags
        if filters.get('tags'):
            queryset = queryset.filter(tags__id__in=filters['tags'])

        # Research field filter
        if filters.get('research_field_id'):
            queryset = queryset.filter(
                research_problems__field_of_science_id=filters['research_field_id']
            )

        # Access condition filters
        if filters.get('access_type'):
            queryset = queryset.filter(
                access_conditions__access_type=filters['access_type'],
                access_conditions__is_active=True
            )

        if filters.get('requires_training') is not None:
            queryset = queryset.filter(
                access_conditions__requires_training=filters['requires_training'],
                access_conditions__is_active=True
            )

        # Pricing filters
        if filters.get('has_pricing'):
            queryset = queryset.filter(
                pricing_policies__is_active=True
            )

        if filters.get('max_price'):
            queryset = queryset.filter(
                Q(pricing_policies__base_price__lte=filters['max_price']) |
                Q(pricing_policies__academic_price__lte=filters['max_price']),
                pricing_policies__is_active=True
            )

        if filters.get('pricing_type'):
            queryset = queryset.filter(
                pricing_policies__pricing_type=filters['pricing_type'],
                pricing_policies__is_active=True
            )

        # Get total count using values_list to avoid duplicates
        total_count = queryset.values_list('id', flat=True).distinct().count()

        # Deduplicate results
        results = SearchService._deduplicate_queryset(queryset)

        # Apply ranking if requested
        if apply_ranking and query_text:
            results = SearchService.rank_results(results, query_text)

        execution_time = int((time.time() - start_time) * 1000)

        return results, execution_time, total_count

    @staticmethod
    def search_equipment(query_text=None, filters=None, apply_ranking=True):
        """
        Search equipment with filters.

        Args:
            query_text: Free text search query
            filters: Dictionary of filter parameters
                - infrastructure_id: Filter by infrastructure
                - city_id: Filter by city
                - status: Equipment status
                - is_available: Filter available
                - condition: Minimum condition rating
                - manufacturer: Filter by manufacturer
                - technology_domains: List of domain IDs
                - tags: List of tag IDs
                - specifications: Dict of specification filters
            apply_ranking: Whether to apply ranking to results (default: True)

        Returns:
            Tuple of (results_list, execution_time_ms, total_count)
        """
        start_time = time.time()
        queryset = Equipment.objects.select_related(
            'infrastructure',
            'infrastructure__institution',
            'infrastructure__city'
        ).prefetch_related(
            'technology_domains',
            'tags',
            'equipment_services',
            'equipment_services__service',
            'specification_values',
            'specification_values__specification'
        )

        filters = filters or {}

        # Text search
        if query_text:
            queryset = queryset.filter(
                Q(translations__name__icontains=query_text) |
                Q(translations__description__icontains=query_text) |
                Q(manufacturer__icontains=query_text) |
                Q(model_number__icontains=query_text) |
                Q(translations__technical_details__icontains=query_text) |
                Q(infrastructure__translations__name__icontains=query_text)
            )

        # Infrastructure filter
        if filters.get('infrastructure_id'):
            queryset = queryset.filter(infrastructure_id=filters['infrastructure_id'])

        # Location filter
        if filters.get('city_id'):
            queryset = queryset.filter(infrastructure__city_id=filters['city_id'])

        # Status filters
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        if 'is_available' in filters:
            queryset = queryset.filter(is_available=filters['is_available'])

        # Condition filter
        if filters.get('condition'):
            queryset = queryset.filter(condition__gte=filters['condition'])

        # Manufacturer filter
        if filters.get('manufacturer'):
            queryset = queryset.filter(manufacturer__icontains=filters['manufacturer'])

        # Technology domains
        if filters.get('technology_domains'):
            queryset = queryset.filter(technology_domains__id__in=filters['technology_domains'])

        # Tags
        if filters.get('tags'):
            queryset = queryset.filter(tags__id__in=filters['tags'])

        # Research field filter
        if filters.get('research_field_id'):
            queryset = queryset.filter(
                infrastructure__research_problems__field_of_science_id=filters['research_field_id']
            )

        # Specification filters
        if filters.get('specifications'):
            for spec_code, value_filter in filters['specifications'].items():
                queryset = queryset.filter(
                    specification_values__specification__code=spec_code
                )

                if 'min' in value_filter:
                    queryset = queryset.filter(
                        Q(specification_values__numeric_value__gte=value_filter['min']) |
                        Q(specification_values__range_min__gte=value_filter['min'])
                    )

                if 'max' in value_filter:
                    queryset = queryset.filter(
                        Q(specification_values__numeric_value__lte=value_filter['max']) |
                        Q(specification_values__range_max__lte=value_filter['max'])
                    )

        # Get total count
        total_count = queryset.values_list('id', flat=True).distinct().count()

        # Deduplicate results
        results = SearchService._deduplicate_queryset(queryset)

        # Apply ranking if requested
        if apply_ranking and query_text:
            results = SearchService.rank_results(results, query_text)

        execution_time = int((time.time() - start_time) * 1000)

        return results, execution_time, total_count

    @staticmethod
    def search_services(query_text=None, filters=None, apply_ranking=True):
        """
        Search services with filters.

        Args:
            query_text: Free text search query
            filters: Dictionary of filter parameters
                - is_active: Filter active services
                - technology_domains: List of domain IDs
                - tags: List of tag IDs
                - max_turnaround_days: Maximum turnaround time
            apply_ranking: Whether to apply ranking to results (default: True)

        Returns:
            Tuple of (results_list, execution_time_ms, total_count)
        """
        start_time = time.time()
        queryset = Service.objects.prefetch_related(
            'technology_domains',
            'tags',
            'equipment_services',
            'equipment_services__equipment',
            'equipment_services__equipment__infrastructure'
        )

        filters = filters or {}

        # Text search
        if query_text:
            queryset = queryset.filter(
                Q(translations__name__icontains=query_text) |
                Q(translations__description__icontains=query_text) |
                Q(translations__methodology__icontains=query_text) |
                Q(translations__typical_applications__icontains=query_text) |
                Q(code__icontains=query_text)
            )

        # Status filter
        if 'is_active' in filters:
            queryset = queryset.filter(is_active=filters['is_active'])

        # Technology domains
        if filters.get('technology_domains'):
            queryset = queryset.filter(technology_domains__id__in=filters['technology_domains'])

        # Tags
        if filters.get('tags'):
            queryset = queryset.filter(tags__id__in=filters['tags'])

        # Turnaround time filter
        if filters.get('max_turnaround_days'):
            queryset = queryset.filter(typical_turnaround_days__lte=filters['max_turnaround_days'])

        # Get total count
        total_count = queryset.values_list('id', flat=True).distinct().count()

        # Deduplicate results
        results = SearchService._deduplicate_queryset(queryset)

        # Apply ranking if requested
        if apply_ranking and query_text:
            results = SearchService.rank_results(results, query_text)

        execution_time = int((time.time() - start_time) * 1000)

        return results, execution_time, total_count

    @staticmethod
    def search_research_problems(query_text=None, filters=None):
        """
        Search research problems with filters.

        Args:
            query_text: Free text search query
            filters: Dictionary of filter parameters
                - field_of_science_id: Filter by field
                - status: Problem status
                - priority: Problem priority
                - is_public: Filter public/private
                - min_complexity: Minimum complexity
                - max_complexity: Maximum complexity

        Returns:
            Tuple of (results_list, execution_time_ms, total_count)
        """
        start_time = time.time()
        queryset = ResearchProblem.objects.select_related(
            'field_of_science'
        ).prefetch_related(
            'additional_fields',
            'keywords',
            'matched_infrastructures'
        )

        filters = filters or {}

        # Text search
        if query_text:
            queryset = queryset.filter(
                Q(translations__title__icontains=query_text) |
                Q(translations__description__icontains=query_text) |
                Q(translations__required_capabilities__icontains=query_text) |
                Q(keywords__translations__name__icontains=query_text)
            )

        # Field of science filter
        if filters.get('field_of_science_id'):
            queryset = queryset.filter(
                Q(field_of_science_id=filters['field_of_science_id']) |
                Q(additional_fields__id=filters['field_of_science_id'])
            )

        # Status filter
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])

        # Priority filter
        if filters.get('priority'):
            queryset = queryset.filter(priority=filters['priority'])

        # Public filter
        if 'is_public' in filters:
            queryset = queryset.filter(is_public=filters['is_public'])

        # Complexity filters
        if filters.get('min_complexity'):
            queryset = queryset.filter(complexity__gte=filters['min_complexity'])
        if filters.get('max_complexity'):
            queryset = queryset.filter(complexity__lte=filters['max_complexity'])

        # Get total count
        total_count = queryset.values_list('id', flat=True).distinct().count()

        # Deduplicate results
        results = SearchService._deduplicate_queryset(queryset)

        execution_time = int((time.time() - start_time) * 1000)

        return results, execution_time, total_count

    @staticmethod
    def unified_search(query_text, search_types=None):
        """
        Unified search across multiple model types.

        Args:
            query_text: Search query
            search_types: List of types to search ['infrastructure', 'equipment', 'service', 'research_problem']

        Returns:
            Dictionary with results from each type
        """
        search_types = search_types or ['infrastructure', 'equipment', 'service']
        results = {}

        if 'infrastructure' in search_types:
            infra_results, time_ms, count = SearchService.search_infrastructures(query_text)
            results['infrastructures'] = {
                'results': infra_results[:10],  # Limit results
                'count': count,
                'time_ms': time_ms
            }

        if 'equipment' in search_types:
            equip_results, time_ms, count = SearchService.search_equipment(query_text)
            results['equipment'] = {
                'results': equip_results[:10],
                'count': count,
                'time_ms': time_ms
            }

        if 'service' in search_types:
            svc_results, time_ms, count = SearchService.search_services(query_text)
            results['services'] = {
                'results': svc_results[:10],
                'count': count,
                'time_ms': time_ms
            }

        if 'research_problem' in search_types:
            prob_results, time_ms, count = SearchService.search_research_problems(query_text)
            results['research_problems'] = {
                'results': prob_results[:10],
                'count': count,
                'time_ms': time_ms
            }

        return results

    @staticmethod
    def rank_results(results, query_text=None, ranking_criteria=None):
        """
        Rank search results based on various criteria.

        Args:
            results: List of search results
            query_text: Original search query
            ranking_criteria: Dictionary of ranking weights
                - relevance_weight: Weight for text match relevance (default: 1.0)
                - reliability_weight: Weight for reliability score (default: 0.3)
                - completeness_weight: Weight for data completeness (default: 0.2)
                - recency_weight: Weight for how recent the data is (default: 0.1)

        Returns:
            Ranked list of results
        """
        if not results:
            return results

        ranking_criteria = ranking_criteria or {
            'relevance_weight': 1.0,
            'reliability_weight': 0.3,
            'completeness_weight': 0.2,
            'recency_weight': 0.1
        }

        scored_results = []

        for obj in results:
            score = 0

            # Relevance score (basic text matching)
            if query_text:
                relevance = 0
                query_lower = query_text.lower()

                # Check name match
                name = getattr(obj, 'name', '') or ''
                if query_lower in name.lower():
                    relevance += 10
                    # Bonus for exact match
                    if query_lower == name.lower():
                        relevance += 20

                # Check description match
                description = getattr(obj, 'description', '') or ''
                if query_lower in description.lower():
                    relevance += 5

                score += relevance * ranking_criteria['relevance_weight']

            # Reliability/quality score
            if hasattr(obj, 'reliability'):
                score += obj.reliability * ranking_criteria['reliability_weight'] * 2

            if hasattr(obj, 'condition'):
                score += obj.condition * ranking_criteria['reliability_weight'] * 2

            # Verification bonus
            if hasattr(obj, 'is_verified') and obj.is_verified:
                score += 5 * ranking_criteria['reliability_weight']

            # Completeness score (basic check)
            completeness = 0
            if hasattr(obj, 'description') and getattr(obj, 'description', None):
                completeness += 2
            if hasattr(obj, 'contact_persons'):
                if obj.contact_persons.exists():
                    completeness += 2
            elif hasattr(obj, 'email') and getattr(obj, 'email', None):
                completeness += 2
            if hasattr(obj, 'documents'):
                if obj.documents.filter(status='active').exists():
                    completeness += 2

            score += completeness * ranking_criteria['completeness_weight']

            # Recency score
            if hasattr(obj, 'updated_at'):
                from django.utils import timezone
                import datetime

                days_old = (timezone.now() - obj.updated_at).days
                # More recent = higher score (max 10 points for updates within 30 days)
                recency_score = max(0, 10 - (days_old / 30 * 10))
                score += recency_score * ranking_criteria['recency_weight']

            scored_results.append((score, obj))

        # Sort by score (descending)
        scored_results.sort(key=lambda x: x[0], reverse=True)

        # Return just the objects
        return [obj for score, obj in scored_results]