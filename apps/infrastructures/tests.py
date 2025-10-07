from django.test import TestCase
from apps.infrastructures.models import Infrastructure, ContactPerson
from apps.institutions.models import Institution
from apps.locations.models import Country, Region, City
from apps.users.models import UserProfile, StaffRole


class InfrastructureModelTest(TestCase):
    """Tests for Infrastructure model."""

    def setUp(self):
        """Set up test data."""
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
            reliability=4,
            is_active=True,
            is_verified=True
        )
        self.infrastructure.set_current_language('en')
        self.infrastructure.name = 'Test Lab'
        self.infrastructure.description = 'A test laboratory'
        self.infrastructure.save()

    def test_infrastructure_creation(self):
        """Test infrastructure is created correctly."""
        self.assertEqual(self.infrastructure.reliability, 4)
        self.assertTrue(self.infrastructure.is_active)
        self.assertTrue(self.infrastructure.is_verified)
        self.assertEqual(Infrastructure.objects.count(), 1)

    def test_infrastructure_str_representation(self):
        """Test infrastructure string representation."""
        self.assertEqual(str(self.infrastructure), 'Test Lab')

    def test_infrastructure_region_property(self):
        """Test infrastructure can access region."""
        self.assertEqual(self.infrastructure.region, self.region)

    def test_infrastructure_country_property(self):
        """Test infrastructure can access country."""
        self.assertEqual(self.infrastructure.country, self.country)

    def test_infrastructure_reliability_choices(self):
        """Test reliability must be between 1-5."""
        self.assertIn(self.infrastructure.reliability, [1, 2, 3, 4, 5])


class ContactPersonModelTest(TestCase):
    """Tests for ContactPerson model."""

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

        # Create contact person
        self.contact = ContactPerson.objects.create(
            infrastructure=self.infrastructure,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            position='Lab Manager',
            is_primary=True
        )

    def test_contact_person_creation(self):
        """Test contact person is created correctly."""
        self.assertEqual(self.contact.first_name, 'John')
        self.assertEqual(self.contact.last_name, 'Doe')
        self.assertEqual(self.contact.email, 'john.doe@example.com')
        self.assertTrue(self.contact.is_primary)

    def test_contact_person_str_representation(self):
        """Test contact person string representation."""
        self.assertIn('John Doe', str(self.contact))

    def test_contact_person_full_name_property(self):
        """Test full_name property."""
        self.assertEqual(self.contact.full_name, 'John Doe')

    def test_contact_person_linked_to_infrastructure(self):
        """Test contact person is linked to infrastructure."""
        self.assertEqual(self.contact.infrastructure, self.infrastructure)
        self.assertIn(self.contact, self.infrastructure.contact_persons.all())