import pytest
from django.contrib.auth import get_user_model
from apps.locations.models import Country, Region, City
from apps.institutions.models import Institution
from apps.infrastructures.models import Infrastructure, ContactPerson

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def superuser(db):
    """Create a test superuser."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def country(db):
    """Create a test country."""
    country = Country.objects.create(code='PL')
    country.set_current_language('en')
    country.name = 'Poland'
    country.save()
    return country


@pytest.fixture
def region(db, country):
    """Create a test region."""
    region = Region.objects.create(country=country, code='MA')
    region.set_current_language('en')
    region.name = 'Lesser Poland'
    region.save()
    return region


@pytest.fixture
def city(db, region):
    """Create a test city."""
    city = City.objects.create(region=region, postal_code='30-000')
    city.set_current_language('en')
    city.name = 'Krakow'
    city.save()
    return city


@pytest.fixture
def institution(db, city):
    """Create a test institution."""
    institution = Institution.objects.create(
        city=city,
        institution_type='university',
        website='https://test.edu.pl',
        email='contact@test.edu.pl'
    )
    institution.set_current_language('en')
    institution.name = 'Test University'
    institution.description = 'A test university'
    institution.save()
    return institution


@pytest.fixture
def infrastructure(db, institution, city):
    """Create a test infrastructure."""
    infra = Infrastructure.objects.create(
        institution=institution,
        city=city,
        reliability=4,
        is_active=True,
        is_verified=True
    )
    infra.set_current_language('en')
    infra.name = 'Test Infrastructure'
    infra.description = 'A test infrastructure'
    infra.save()
    return infra