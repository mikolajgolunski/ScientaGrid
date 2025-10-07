from django.test import TestCase
from decimal import Decimal
from apps.services.models import Service, EquipmentService
from apps.equipment.models import Equipment
from apps.infrastructures.models import Infrastructure
from apps.institutions.models import Institution
from apps.locations.models import Country, Region, City


class ServiceModelTest(TestCase):
    """Tests for Service model."""

    def setUp(self):
        """Set up test data."""
        self.service = Service.objects.create(
            code='TEST-001',
            typical_turnaround_days=7,
            is_active=True
        )
        self.service.set_current_language('en')
        self.service.name = 'Test Analysis Service'
        self.service.description = 'A comprehensive test analysis service'
        self.service.methodology = 'Advanced testing methodology'
        self.service.save()

    def test_service_creation(self):
        """Test service is created correctly."""
        self.assertEqual(self.service.code, 'TEST-001')
        self.assertEqual(self.service.typical_turnaround_days, 7)
        self.assertTrue(self.service.is_active)
        self.assertEqual(Service.objects.count(), 1)

    def test_service_str_representation(self):
        """Test service string representation."""
        self.assertIn('Test Analysis Service', str(self.service))
        self.assertIn('TEST-001', str(self.service))

    def test_service_without_code(self):
        """Test service can exist without code."""
        service = Service.objects.create(is_active=True)
        service.set_current_language('en')
        service.name = 'No Code Service'
        service.save()

        self.assertEqual(str(service), 'No Code Service')


class EquipmentServiceTest(TestCase):
    """Tests for EquipmentService model."""

    def setUp(self):
        """Set up test data."""
        # Create location hierarchy
        country = Country.objects.create(code='PL')
        country.set_current_language('en')
        country.name = 'Poland'
        country.save()

        region = Region.objects.create(country=country, code='MA')
        region.set_current_language('en')
        region.name = 'Lesser Poland'
        region.save()

        city = City.objects.create(region=region)
        city.set_current_language('en')
        city.name = 'Krakow'
        city.save()

        # Create institution
        institution = Institution.objects.create(city=city)
        institution.set_current_language('en')
        institution.name = 'Test University'
        institution.save()

        # Create infrastructure
        infrastructure = Infrastructure.objects.create(
            institution=institution,
            city=city
        )
        infrastructure.set_current_language('en')
        infrastructure.name = 'Test Lab'
        infrastructure.save()

        # Create equipment
        self.equipment = Equipment.objects.create(
            infrastructure=infrastructure,
            manufacturer='TestCo',
            model_number='TM-100',
            status='operational',
            is_available=True
        )
        self.equipment.set_current_language('en')
        self.equipment.name = 'Test Equipment'
        self.equipment.save()

        # Create service
        self.service = Service.objects.create(code='SVC-001')
        self.service.set_current_language('en')
        self.service.name = 'Analysis Service'
        self.service.save()

        # Create equipment-service link
        self.eq_service = EquipmentService.objects.create(
            equipment=self.equipment,
            service=self.service,
            estimated_cost=Decimal('500.00'),
            capacity_per_day=10,
            is_primary=True,
            is_available=True,
            notes='Standard service offering'
        )

    def test_equipment_service_creation(self):
        """Test equipment-service link is created correctly."""
        self.assertEqual(self.eq_service.equipment, self.equipment)
        self.assertEqual(self.eq_service.service, self.service)
        self.assertEqual(self.eq_service.estimated_cost, Decimal('500.00'))
        self.assertEqual(self.eq_service.capacity_per_day, 10)
        self.assertTrue(self.eq_service.is_primary)
        self.assertTrue(self.eq_service.is_available)

    def test_equipment_service_str_representation(self):
        """Test equipment-service string representation."""
        self.assertIn('Test Equipment', str(self.eq_service))
        self.assertIn('Analysis Service', str(self.eq_service))

    def test_equipment_service_infrastructure_property(self):
        """Test can access infrastructure through equipment."""
        self.assertEqual(self.eq_service.infrastructure, self.equipment.infrastructure)

    def test_equipment_service_full_location_property(self):
        """Test full location property."""
        location = self.eq_service.full_location
        self.assertIn('Test Lab', location)
        self.assertIn('Krakow', location)

    def test_equipment_service_unique_constraint(self):
        """Test equipment-service combination must be unique."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            EquipmentService.objects.create(
                equipment=self.equipment,
                service=self.service
            )
