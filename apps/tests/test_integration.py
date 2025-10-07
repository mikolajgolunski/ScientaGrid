from django.test import TestCase
from apps.locations.models import Country, Region, City
from apps.institutions.models import Institution
from apps.infrastructures.models import Infrastructure, ContactPerson
from apps.equipment.models import Equipment
from apps.services.models import Service, EquipmentService
from apps.access.models import AccessCondition, PricingPolicy
from apps.taxonomy.models import TechnologyDomain, Tag
from apps.specifications.models import Specification, SpecificationValue
from apps.search.services import SearchService
from decimal import Decimal


class FullWorkflowIntegrationTest(TestCase):
    """Integration test for complete workflow."""

    def setUp(self):
        """Set up complete test data."""
        # Create location
        self.country = Country.objects.create(code='PL')
        self.country.set_current_language('en')
        self.country.name = 'Poland'
        self.country.save()

        self.region = Region.objects.create(country=self.country, code='MA')
        self.region.set_current_language('en')
        self.region.name = 'Lesser Poland'
        self.region.save()

        self.city = City.objects.create(region=self.region)
        self.city.set_current_language('en')
        self.city.name = 'Krakow'
        self.city.save()

        # Create institution
        self.institution = Institution.objects.create(
            city=self.city,
            institution_type='university'
        )
        self.institution.set_current_language('en')
        self.institution.name = 'Test University'
        self.institution.save()

        # Create infrastructure
        self.infrastructure = Infrastructure.objects.create(
            institution=self.institution,
            city=self.city,
            reliability=5,
            is_active=True,
            is_verified=True
        )
        self.infrastructure.set_current_language('en')
        self.infrastructure.name = 'Advanced Microscopy Lab'
        self.infrastructure.description = 'State-of-the-art microscopy facility'
        self.infrastructure.save()

        # Create contact person
        self.contact = ContactPerson.objects.create(
            infrastructure=self.infrastructure,
            first_name='John',
            last_name='Doe',
            email='john.doe@test.edu',
            is_primary=True
        )

        # Create equipment
        self.equipment = Equipment.objects.create(
            infrastructure=self.infrastructure,
            manufacturer='JEOL',
            model_number='TEM-2100',
            status='operational',
            is_available=True,
            condition=5
        )
        self.equipment.set_current_language('en')
        self.equipment.name = 'Transmission Electron Microscope'
        self.equipment.description = 'High-resolution TEM'
        self.equipment.save()

        # Create service
        self.service = Service.objects.create(
            code='TEM-IMG',
            typical_turnaround_days=7,
            is_active=True
        )
        self.service.set_current_language('en')
        self.service.name = 'TEM Imaging Service'
        self.service.save()

        # Link equipment and service
        self.eq_service = EquipmentService.objects.create(
            equipment=self.equipment,
            service=self.service,
            estimated_cost=Decimal('500.00'),
            is_primary=True,
            is_available=True
        )

        # Create access condition
        self.access = AccessCondition.objects.create(
            infrastructure=self.infrastructure,
            access_type='by_approval',
            requires_training=True,
            is_active=True
        )
        self.access.set_current_language('en')
        self.access.name = 'Standard Access'
        self.access.save()

        # Create pricing
        self.pricing = PricingPolicy.objects.create(
            infrastructure=self.infrastructure,
            pricing_type='per_hour',
            base_price=Decimal('200.00'),
            academic_price=Decimal('100.00'),
            is_active=True
        )
        self.pricing.set_current_language('en')
        self.pricing.name = 'Hourly Rate'
        self.pricing.save()

        # Create taxonomy
        self.domain = TechnologyDomain.objects.create(code='PHYS')
        self.domain.set_current_language('en')
        self.domain.name = 'Physics'
        self.domain.save()

        self.infrastructure.technology_domains.add(self.domain)

        self.tag = Tag.objects.create(slug='microscopy', tag_type='technique')
        self.tag.set_current_language('en')
        self.tag.name = 'Microscopy'
        self.tag.save()

        self.infrastructure.tags.add(self.tag)
        self.equipment.tags.add(self.tag)

        # Create specification
        self.spec = Specification.objects.create(
            code='RESOLUTION',
            data_type='numeric',
            unit='nm'
        )
        self.spec.set_current_language('en')
        self.spec.name = 'Resolution'
        self.spec.save()

        self.spec_value = SpecificationValue.objects.create(
            equipment=self.equipment,
            specification=self.spec,
            numeric_value=Decimal('0.19'),
            is_verified=True
        )

    def test_complete_infrastructure_setup(self):
        """Test complete infrastructure is set up correctly."""
        # Verify all components exist
        self.assertEqual(Infrastructure.objects.count(), 1)
        self.assertEqual(Equipment.objects.count(), 1)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(EquipmentService.objects.count(), 1)
        self.assertEqual(AccessCondition.objects.count(), 1)
        self.assertEqual(PricingPolicy.objects.count(), 1)

    def test_infrastructure_relationships(self):
        """Test all relationships are properly linked."""
        # Test infrastructure relationships
        self.assertEqual(self.infrastructure.institution, self.institution)
        self.assertEqual(self.infrastructure.city, self.city)
        self.assertEqual(self.infrastructure.contact_persons.count(), 1)
        self.assertEqual(self.infrastructure.equipment.count(), 1)

        # Test equipment relationships
        self.assertEqual(self.equipment.infrastructure, self.infrastructure)
        self.assertEqual(self.equipment.specification_values.count(), 1)

        # Test service relationships
        self.assertIn(self.equipment, self.service.equipment_services.values_list('equipment', flat=True))

    def test_search_finds_infrastructure(self):
        """Test search can find the infrastructure."""
        results, time_ms, count = SearchService.search_infrastructures('microscopy')

        self.assertEqual(count, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.infrastructure)

    def test_search_finds_equipment(self):
        """Test search can find the equipment."""
        results, time_ms, count = SearchService.search_equipment('TEM')

        self.assertEqual(count, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.equipment)

    def test_search_by_location(self):
        """Test search can filter by location."""
        filters = {'city_id': self.city.id}
        results, time_ms, count = SearchService.search_infrastructures(filters=filters)

        self.assertEqual(count, 1)
        self.assertIn(self.infrastructure, results)

    def test_search_by_taxonomy(self):
        """Test search can filter by taxonomy."""
        filters = {'technology_domains': [self.domain.id]}
        results, time_ms, count = SearchService.search_infrastructures(filters=filters)

        self.assertEqual(count, 1)
        self.assertIn(self.infrastructure, results)

    def test_unified_search(self):
        """Test unified search across all types."""
        results = SearchService.unified_search('microscopy')

        self.assertIn('infrastructures', results)
        self.assertIn('equipment', results)
        self.assertIn('services', results)

        self.assertEqual(results['infrastructures']['count'], 1)
        self.assertEqual(results['equipment']['count'], 1)
        self.assertEqual(results['services']['count'], 1)