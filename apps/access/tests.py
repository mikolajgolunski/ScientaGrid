from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from apps.access.models import AccessCondition, PricingPolicy
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment
from apps.services.models import Service
from apps.institutions.models import Institution
from apps.locations.models import Country, Region, City


class AccessConditionModelTest(TestCase):
    """Tests for AccessCondition model."""

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

        # Create access condition
        self.access_condition = AccessCondition.objects.create(
            infrastructure=self.infrastructure,
            access_type='by_approval',
            requires_booking=True,
            min_booking_days=7,
            max_booking_days=90,
            requires_training=True,
            training_duration_hours=4,
            is_active=True
        )
        self.access_condition.set_current_language('en')
        self.access_condition.name = 'Standard Access'
        self.access_condition.description = 'Standard access conditions'
        self.access_condition.save()

    def test_access_condition_creation(self):
        """Test access condition is created correctly."""
        self.assertEqual(self.access_condition.access_type, 'by_approval')
        self.assertTrue(self.access_condition.requires_booking)
        self.assertEqual(self.access_condition.min_booking_days, 7)
        self.assertTrue(self.access_condition.requires_training)
        self.assertEqual(AccessCondition.objects.count(), 1)

    def test_access_condition_str_representation(self):
        """Test access condition string representation."""
        self.assertIn('Standard Access', str(self.access_condition))

    def test_access_condition_validation_requires_object(self):
        """Test access condition must be linked to at least one object."""
        ac = AccessCondition(
            access_type='open',
            is_active=True
        )
        ac.set_current_language('en')
        ac.name = 'Invalid Access'

        with self.assertRaises(ValidationError):
            ac.full_clean()

    def test_access_type_choices(self):
        """Test access_type is one of valid choices."""
        valid_types = ['open', 'restricted', 'by_approval', 'commercial', 'academic', 'collaborative']
        self.assertIn(self.access_condition.access_type, valid_types)


class PricingPolicyModelTest(TestCase):
    """Tests for PricingPolicy model."""

    def setUp(self):
        """Set up test data."""
        # Create minimal infrastructure
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

        # Create pricing policy
        self.pricing = PricingPolicy.objects.create(
            infrastructure=self.infrastructure,
            pricing_type='per_hour',
            base_price=Decimal('200.00'),
            academic_price=Decimal('100.00'),
            commercial_price=Decimal('500.00'),
            internal_price=Decimal('50.00'),
            includes_operator=True,
            includes_analysis=False,
            valid_from=date(2025, 1, 1),
            is_active=True
        )
        self.pricing.set_current_language('en')
        self.pricing.name = 'Standard Hourly Rate'
        self.pricing.description = 'Standard pricing for facility access'
        self.pricing.save()

    def test_pricing_policy_creation(self):
        """Test pricing policy is created correctly."""
        self.assertEqual(self.pricing.pricing_type, 'per_hour')
        self.assertEqual(self.pricing.base_price, Decimal('200.00'))
        self.assertEqual(self.pricing.academic_price, Decimal('100.00'))
        self.assertTrue(self.pricing.includes_operator)
        self.assertEqual(PricingPolicy.objects.count(), 1)

    def test_pricing_policy_str_representation(self):
        """Test pricing policy string representation."""
        self.assertIn('Standard Hourly Rate', str(self.pricing))
        self.assertIn('200', str(self.pricing))

    def test_pricing_policy_validation_requires_object(self):
        """Test pricing policy must be linked to at least one object."""
        pp = PricingPolicy(
            pricing_type='free',
            is_active=True
        )
        pp.set_current_language('en')
        pp.name = 'Invalid Pricing'

        with self.assertRaises(ValidationError):
            pp.full_clean()

    def test_pricing_type_choices(self):
        """Test pricing_type is one of valid choices."""
        valid_types = ['free', 'per_hour', 'per_day', 'per_sample', 'per_measurement', 'per_project', 'custom']
        self.assertIn(self.pricing.pricing_type, valid_types)
