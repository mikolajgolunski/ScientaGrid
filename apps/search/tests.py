from django.test import TestCase
from apps.search.services import SearchService
from apps.search.models import SavedSearch, SearchLog
from apps.users.models import UserProfile, StaffRole
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment
from apps.institutions.models import Institution
from apps.locations.models import Country, Region, City


class SearchServiceTest(TestCase):
    """Tests for SearchService."""

    def setUp(self):
        """Set up test data."""
        # Create location
        country = Country.objects.create(code='PL')
        country.set_current_language('en')
        country.name = 'Poland'
        country.save()

        region = Region.objects.create(country=country, code='MA')
        region.set_current_language('en')
        region.name = 'Lesser Poland'
        region.save()

        self.city = City.objects.create(region=region)
        self.city.set_current_language('en')
        self.city.name = 'Krakow'
        self.city.save()

        # Create institution
        institution = Institution.objects.create(city=self.city)
        institution.set_current_language('en')
        institution.name = 'Test University'
        institution.save()

        # Create infrastructures
        self.infra1 = Infrastructure.objects.create(
            institution=institution,
            city=self.city,
            is_active=True
        )
        self.infra1.set_current_language('en')
        self.infra1.name = 'Microscopy Lab'
        self.infra1.description = 'Advanced microscopy facility'
        self.infra1.save()

        self.infra2 = Infrastructure.objects.create(
            institution=institution,
            city=self.city,
            is_active=True
        )
        self.infra2.set_current_language('en')
        self.infra2.name = 'Spectroscopy Lab'
        self.infra2.description = 'Spectroscopy analysis center'
        self.infra2.save()

        # Create equipment
        self.equipment = Equipment.objects.create(
            infrastructure=self.infra1,
            manufacturer='TestCo',
            model_number='TEM-100',
            status='operational',
            is_available=True
        )
        self.equipment.set_current_language('en')
        self.equipment.name = 'Electron Microscope'
        self.equipment.description = 'High-resolution TEM'
        self.equipment.save()

    def test_search_infrastructures_by_text(self):
        """Test searching infrastructures by text."""
        results, time_ms, count = SearchService.search_infrastructures('microscopy')

        self.assertEqual(count, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.infra1)

    def test_search_infrastructures_by_city(self):
        """Test searching infrastructures by city."""
        filters = {'city_id': self.city.id}
        results, time_ms, count = SearchService.search_infrastructures(filters=filters)

        self.assertEqual(count, 2)
        self.assertEqual(len(results), 2)

    def test_search_equipment_by_text(self):
        """Test searching equipment by text."""
        results, time_ms, count = SearchService.search_equipment('microscope')

        self.assertEqual(count, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.equipment)

    def test_search_equipment_by_model(self):
        """Test searching equipment by model number."""
        results, time_ms, count = SearchService.search_equipment('TEM-100')

        self.assertEqual(count, 1)
        self.assertEqual(len(results), 1)

    def test_unified_search(self):
        """Test unified search across types."""
        results = SearchService.unified_search('microscopy')

        self.assertIn('infrastructures', results)
        self.assertIn('equipment', results)
        self.assertEqual(results['infrastructures']['count'], 1)
        self.assertEqual(results['equipment']['count'], 1)

    def test_search_no_results(self):
        """Test search with no results."""
        results, time_ms, count = SearchService.search_infrastructures('nonexistent')

        self.assertEqual(count, 0)
        self.assertEqual(len(results), 0)

    def test_search_case_insensitive(self):
        """Test search is case insensitive."""
        results1, _, count1 = SearchService.search_infrastructures('MICROSCOPY')
        results2, _, count2 = SearchService.search_infrastructures('microscopy')

        self.assertEqual(count1, count2)
        self.assertEqual(len(results1), len(results2))


class SavedSearchModelTest(TestCase):
    """Tests for SavedSearch model."""

    def setUp(self):
        """Set up test data."""
        # Create user
        role = StaffRole.objects.create(name='admin')
        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            staff_role=role
        )

        # Create saved search
        self.saved_search = SavedSearch.objects.create(
            user=self.user,
            name='My Microscopy Search',
            description='Search for microscopy equipment',
            search_params={'query_text': 'microscopy', 'city_id': 1},
            search_type='equipment',
            usage_count=0,
            notify_on_new_results=False,
            is_active=True
        )

    def test_saved_search_creation(self):
        """Test saved search is created correctly."""
        self.assertEqual(self.saved_search.user, self.user)
        self.assertEqual(self.saved_search.name, 'My Microscopy Search')
        self.assertEqual(self.saved_search.search_type, 'equipment')
        self.assertEqual(self.saved_search.usage_count, 0)
        self.assertEqual(SavedSearch.objects.count(), 1)

    def test_saved_search_str_representation(self):
        """Test saved search string representation."""
        self.assertIn('testuser', str(self.saved_search))
        self.assertIn('My Microscopy Search', str(self.saved_search))

    def test_saved_search_get_params_dict(self):
        """Test get_params_dict method."""
        params = self.saved_search.get_params_dict()
        self.assertIsInstance(params, dict)
        self.assertEqual(params['query_text'], 'microscopy')
        self.assertEqual(params['city_id'], 1)

    def test_saved_search_increment_usage(self):
        """Test increment_usage method."""
        initial_count = self.saved_search.usage_count
        self.saved_search.increment_usage()

        self.assertEqual(self.saved_search.usage_count, initial_count + 1)
        self.assertIsNotNone(self.saved_search.last_used_at)


class SearchLogModelTest(TestCase):
    """Tests for SearchLog model."""

    def setUp(self):
        """Set up test data."""
        # Create user
        role = StaffRole.objects.create(name='admin')
        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            staff_role=role
        )

        # Create search log
        self.search_log = SearchLog.objects.create(
            user=self.user,
            query_text='microscopy',
            filters={'city_id': 1, 'is_active': True},
            search_type='equipment',
            results_count=5,
            execution_time_ms=125,
            session_id='test-session-123'
        )

    def test_search_log_creation(self):
        """Test search log is created correctly."""
        self.assertEqual(self.search_log.user, self.user)
        self.assertEqual(self.search_log.query_text, 'microscopy')
        self.assertEqual(self.search_log.search_type, 'equipment')
        self.assertEqual(self.search_log.results_count, 5)
        self.assertEqual(self.search_log.execution_time_ms, 125)
        self.assertEqual(SearchLog.objects.count(), 1)

    def test_search_log_str_representation(self):
        """Test search log string representation."""
        self.assertIn('testuser', str(self.search_log))
        self.assertIn('microscopy', str(self.search_log))
