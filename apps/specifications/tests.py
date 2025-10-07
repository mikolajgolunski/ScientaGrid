from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.specifications.models import Specification, SpecificationValue
from apps.equipment.models import Equipment
from apps.infrastructures.models import Infrastructure
from apps.institutions.models import Institution
from apps.locations.models import Country, Region, City


class SpecificationModelTest(TestCase):
    """Tests for Specification model."""

    def setUp(self):
        """Set up test data."""
        self.spec_numeric = Specification.objects.create(
            code='RESOLUTION',
            data_type='numeric',
            unit='nm',
            category='performance',
            display_order=10,
            is_filterable=True,
            is_active=True
        )
        self.spec_numeric.set_current_language('en')
        self.spec_numeric.name = 'Resolution'
        self.spec_numeric.description = 'Maximum resolution'
        self.spec_numeric.unit_label = 'nanometers'
        self.spec_numeric.save()

        self.spec_choice = Specification.objects.create(
            code='SAMPLE_TYPE',
            data_type='choice',
            choices='Solid, Liquid, Gas',
            category='sample',
            is_active=True
        )
        self.spec_choice.set_current_language('en')
        self.spec_choice.name = 'Sample Type'
        self.spec_choice.save()

    def test_specification_creation(self):
        """Test specification is created correctly."""
        self.assertEqual(self.spec_numeric.code, 'RESOLUTION')
        self.assertEqual(self.spec_numeric.data_type, 'numeric')
        self.assertEqual(self.spec_numeric.unit, 'nm')
        self.assertEqual(Specification.objects.count(), 2)

    def test_specification_str_representation(self):
        """Test specification string representation."""
        self.assertIn('Resolution', str(self.spec_numeric))
        self.assertIn('nm', str(self.spec_numeric))

    def test_specification_get_choices_list(self):
        """Test get_choices_list method."""
        choices = self.spec_choice.get_choices_list()
        self.assertEqual(len(choices), 3)
        self.assertIn('Solid', choices)
        self.assertIn('Liquid', choices)
        self.assertIn('Gas', choices)


class SpecificationValueModelTest(TestCase):
    """Tests for SpecificationValue model."""

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
            status='operational'
        )
        self.equipment.set_current_language('en')
        self.equipment.name = 'Test Equipment'
        self.equipment.save()

        # Create specifications
        self.spec_numeric = Specification.objects.create(
            code='RESOLUTION',
            data_type='numeric',
            unit='nm'
        )
        self.spec_numeric.set_current_language('en')
        self.spec_numeric.name = 'Resolution'
        self.spec_numeric.save()

        self.spec_range = Specification.objects.create(
            code='TEMP_RANGE',
            data_type='range',
            unit='°C'
        )
        self.spec_range.set_current_language('en')
        self.spec_range.name = 'Temperature Range'
        self.spec_range.save()

        self.spec_boolean = Specification.objects.create(
            code='AUTOMATED',
            data_type='boolean'
        )
        self.spec_boolean.set_current_language('en')
        self.spec_boolean.name = 'Automated'
        self.spec_boolean.save()

        # Create specification values
        self.value_numeric = SpecificationValue.objects.create(
            equipment=self.equipment,
            specification=self.spec_numeric,
            numeric_value=Decimal('0.5'),
            is_verified=True
        )

        self.value_range = SpecificationValue.objects.create(
            equipment=self.equipment,
            specification=self.spec_range,
            range_min=Decimal('-20'),
            range_max=Decimal('100'),
            is_verified=True
        )

        self.value_boolean = SpecificationValue.objects.create(
            equipment=self.equipment,
            specification=self.spec_boolean,
            boolean_value=True,
            is_verified=False
        )

    def test_specification_value_creation(self):
        """Test specification value is created correctly."""
        self.assertEqual(self.value_numeric.equipment, self.equipment)
        self.assertEqual(self.value_numeric.specification, self.spec_numeric)
        self.assertEqual(self.value_numeric.numeric_value, Decimal('0.5'))
        self.assertTrue(self.value_numeric.is_verified)
        self.assertEqual(SpecificationValue.objects.count(), 3)

    def test_specification_value_str_representation(self):
        """Test specification value string representation."""
        self.assertIn('Test Equipment', str(self.value_numeric))
        self.assertIn('Resolution', str(self.value_numeric))

    def test_get_display_value_numeric(self):
        """Test get_display_value for numeric type."""
        display = self.value_numeric.get_display_value()
        self.assertIn('0.5', display)
        self.assertIn('nm', display)

    def test_get_display_value_range(self):
        """Test get_display_value for range type."""
        display = self.value_range.get_display_value()
        self.assertIn('-20', display)
        self.assertIn('100', display)
        self.assertIn('°C', display)

    def test_get_display_value_boolean(self):
        """Test get_display_value for boolean type."""
        display = self.value_boolean.get_display_value()
        self.assertEqual(display, 'Yes')

    def test_specification_value_unique_constraint(self):
        """Test equipment-specification combination must be unique."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            SpecificationValue.objects.create(
                equipment=self.equipment,
                specification=self.spec_numeric,
                numeric_value=Decimal('1.0')
            )
