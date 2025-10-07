from django.test import TestCase
from apps.locations.models import Country, Region, City


class CountryModelTest(TestCase):
    """Tests for Country model."""

    def setUp(self):
        """Set up test data."""
        self.country = Country.objects.create(code='PL')
        self.country.set_current_language('en')
        self.country.name = 'Poland'
        self.country.set_current_language('pl')
        self.country.name = 'Polska'
        self.country.save()

    def test_country_creation(self):
        """Test country is created correctly."""
        self.assertEqual(self.country.code, 'PL')
        self.assertEqual(Country.objects.count(), 1)

    def test_country_str_representation(self):
        """Test country string representation."""
        self.assertEqual(str(self.country), 'Polska')

    def test_country_translation(self):
        """Test country translations work."""
        self.country.set_current_language('en')
        self.assertEqual(self.country.name, 'Poland')
        self.country.set_current_language('pl')
        self.assertEqual(self.country.name, 'Polska')

    def test_country_code_unique(self):
        """Test country code must be unique."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Country.objects.create(code='PL')


class RegionModelTest(TestCase):
    """Tests for Region model."""

    def setUp(self):
        """Set up test data."""
        self.country = Country.objects.create(code='PL')
        self.country.set_current_language('en')
        self.country.name = 'Poland'
        self.country.save()

        self.region = Region.objects.create(country=self.country, code='MA')
        self.region.set_current_language('en')
        self.region.name = 'Lesser Poland'
        self.region.save()

    def test_region_creation(self):
        """Test region is created correctly."""
        self.assertEqual(self.region.code, 'MA')
        self.assertEqual(self.region.country, self.country)
        self.assertEqual(Region.objects.count(), 1)

    def test_region_str_representation(self):
        """Test region string representation."""
        self.assertEqual(str(self.region), 'Lesser Poland')

    def test_region_belongs_to_country(self):
        """Test region is linked to country."""
        self.assertEqual(self.region.country, self.country)
        self.assertIn(self.region, self.country.regions.all())


class CityModelTest(TestCase):
    """Tests for City model."""

    def setUp(self):
        """Set up test data."""
        self.country = Country.objects.create(code='PL')
        self.country.set_current_language('en')
        self.country.name = 'Poland'
        self.country.save()

        self.region = Region.objects.create(country=self.country, code='MA')
        self.region.set_current_language('en')
        self.region.name = 'Lesser Poland'
        self.region.save()

        self.city = City.objects.create(
            region=self.region,
            postal_code='30-000'
        )
        self.city.set_current_language('en')
        self.city.name = 'Krakow'
        self.city.save()

    def test_city_creation(self):
        """Test city is created correctly."""
        self.assertEqual(self.city.postal_code, '30-000')
        self.assertEqual(self.city.region, self.region)
        self.assertEqual(City.objects.count(), 1)

    def test_city_str_representation(self):
        """Test city string representation."""
        self.assertEqual(str(self.city), 'Krakow')

    def test_city_country_property(self):
        """Test city can access country through region."""
        self.assertEqual(self.city.country, self.country)