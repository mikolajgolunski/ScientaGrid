from django.test import TestCase
from apps.equipment.models import Equipment
from apps.infrastructures.models import Infrastructure
from apps.institutions.models import Institution
from apps.locations.models import Country, Region, City


class EquipmentModelTest(TestCase):
    """Tests for Equipment model."""

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

        institution = Institution.objects.create(city=city)
        institution.set_current_language('en')
        institution.name = 'Test University'
        institution.save()

        self.infrastructure = Infrastructure.objects.create(
            institution=institution,
            city=city
        )
        self.infrastructure.set_current_language('en')
        self.infrastructure.name = 'Test Lab'
        self.infrastructure.save()

        # Create equipment
        self.equipment = Equipment.objects.create(
            infrastructure=self.infrastructure,
            manufacturer='Test Manufacturer',
            model_number='TM-100',
            serial_number='SN123456',
            year_of_purchase=2020,
            status='operational',
            is_available=True,
            condition=4,
            requires_training=True
        )
        self.equipment.set_current_language('en')
        self.equipment.name = 'Test Microscope'
        self.equipment.description = 'A test microscope'
        self.equipment.save()

    def test_equipment_creation(self):
        """Test equipment is created correctly."""
        self.assertEqual(self.equipment.manufacturer, 'Test Manufacturer')
        self.assertEqual(self.equipment.model_number, 'TM-100')
        self.assertEqual(self.equipment.status, 'operational')
        self.assertTrue(self.equipment.is_available)
        self.assertEqual(Equipment.objects.count(), 1)

    def test_equipment_str_representation(self):
        """Test equipment string representation."""
        self.assertIn('Test Microscope', str(self.equipment))
        self.assertIn('TM-100', str(self.equipment))

    def test_equipment_institution_property(self):
        """Test equipment can access institution."""
        self.assertEqual(self.equipment.institution, self.infrastructure.institution)

    def test_equipment_city_property(self):
        """Test equipment can access city."""
        self.assertEqual(self.equipment.city, self.infrastructure.city)

    def test_equipment_full_location_property(self):
        """Test full_location property."""
        self.assertIn('Test Lab', self.equipment.full_location)
        self.assertIn('Krakow', self.equipment.full_location)

    def test_equipment_status_choices(self):
        """Test status is one of the valid choices."""
        valid_statuses = ['operational', 'maintenance', 'out_of_order', 'reserved', 'decommissioned']
        self.assertIn(self.equipment.status, valid_statuses)