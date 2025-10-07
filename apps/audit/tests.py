from django.test import TestCase
from apps.audit.models import AuditLog, ChangeHistory, DataQualityMetric
from apps.infrastructures.models import Infrastructure
from apps.institutions.models import Institution
from apps.locations.models import Country, Region, City
from apps.users.models import UserProfile, StaffRole


class AuditLogTest(TestCase):
    """Tests for AuditLog model."""

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

        # Create infrastructure
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

    def test_audit_log_creation(self):
        """Test audit log can be created."""
        log = AuditLog.log_action(
            action_type='create',
            user=self.user,
            content_object=self.infrastructure,
            description='Created infrastructure',
            category='infrastructure'
        )

        self.assertEqual(log.action_type, 'create')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.category, 'infrastructure')
        self.assertIn('Test Lab', log.object_repr)

    def test_audit_log_str_representation(self):
        """Test audit log string representation."""
        log = AuditLog.log_action(
            action_type='update',
            user=self.user,
            content_object=self.infrastructure
        )

        log_str = str(log)
        self.assertIn('testuser', log_str)
        self.assertIn('Updated', log_str)


class ChangeHistoryTest(TestCase):
    """Tests for ChangeHistory model."""

    def setUp(self):
        """Set up test data."""
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
            city=city,
            reliability=3
        )
        self.infrastructure.set_current_language('en')
        self.infrastructure.name = 'Test Lab'
        self.infrastructure.save()

    def test_change_history_creation(self):
        """Test change history can be logged."""
        change = ChangeHistory.log_change(
            content_object=self.infrastructure,
            field_name='reliability',
            old_value=3,
            new_value=4,
            change_type='update'
        )

        self.assertEqual(change.field_name, 'reliability')
        self.assertEqual(change.old_value, '3')
        self.assertEqual(change.new_value, '4')
        self.assertEqual(change.change_type, 'update')


class DataQualityMetricTest(TestCase):
    """Tests for DataQualityMetric model."""

    def setUp(self):
        """Set up test data."""
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

        institution = Institution.objects.create(city=city, email='test@test.edu')
        institution.set_current_language('en')
        institution.name = 'Test University'
        institution.description = 'A test university'
        institution.save()

        self.infrastructure = Infrastructure.objects.create(
            institution=institution,
            city=city,
            email='lab@test.edu'
        )
        self.infrastructure.set_current_language('en')
        self.infrastructure.name = 'Test Lab'
        self.infrastructure.description = 'A comprehensive test laboratory'
        self.infrastructure.save()

    def test_calculate_quality_metric(self):
        """Test quality metric calculation."""
        metric = DataQualityMetric.calculate_for_object(self.infrastructure)

        self.assertIsNotNone(metric.quality_score)
        self.assertIsNotNone(metric.completeness_score)
        self.assertTrue(0 <= metric.quality_score <= 100)
        self.assertTrue(0 <= metric.completeness_score <= 100)

    def test_quality_level_property(self):
        """Test quality level property."""
        metric = DataQualityMetric.calculate_for_object(self.infrastructure)

        quality_levels = ['Poor', 'Fair', 'Good', 'Excellent']
        self.assertIn(metric.quality_level, quality_levels)