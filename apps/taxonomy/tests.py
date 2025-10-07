from django.test import TestCase
from apps.taxonomy.models import TechnologyDomain, InfrastructureCategory, Tag
from apps.infrastructures.models import Infrastructure
from apps.institutions.models import Institution
from apps.locations.models import Country, Region, City


class TechnologyDomainModelTest(TestCase):
    """Tests for TechnologyDomain model."""

    def setUp(self):
        """Set up test data."""
        # Create parent domain
        self.parent_domain = TechnologyDomain.objects.create(
            code='PHYS',
            is_active=True
        )
        self.parent_domain.set_current_language('en')
        self.parent_domain.name = 'Physics'
        self.parent_domain.description = 'Physical sciences'
        self.parent_domain.save()

        # Create child domain
        self.child_domain = TechnologyDomain.objects.create(
            code='PHYS-NANO',
            parent=self.parent_domain,
            is_active=True
        )
        self.child_domain.set_current_language('en')
        self.child_domain.name = 'Nanophysics'
        self.child_domain.description = 'Physics at nanoscale'
        self.child_domain.save()

    def test_technology_domain_creation(self):
        """Test technology domain is created correctly."""
        self.assertEqual(self.parent_domain.code, 'PHYS')
        self.assertTrue(self.parent_domain.is_active)
        self.assertEqual(TechnologyDomain.objects.count(), 2)

    def test_technology_domain_str_representation(self):
        """Test technology domain string representation."""
        self.assertIn('PHYS', str(self.parent_domain))
        self.assertIn('Physics', str(self.parent_domain))

    def test_technology_domain_hierarchy(self):
        """Test hierarchical relationship."""
        self.assertEqual(self.child_domain.parent, self.parent_domain)
        self.assertIn(self.child_domain, self.parent_domain.subdomains.all())

    def test_technology_domain_level_property(self):
        """Test level property for hierarchy."""
        self.assertEqual(self.parent_domain.level, 0)
        self.assertEqual(self.child_domain.level, 1)

    def test_technology_domain_full_path_property(self):
        """Test full_path property."""
        self.assertEqual(self.parent_domain.full_path, 'Physics')
        self.assertIn('Physics', self.child_domain.full_path)
        self.assertIn('Nanophysics', self.child_domain.full_path)


class InfrastructureCategoryModelTest(TestCase):
    """Tests for InfrastructureCategory model."""

    def setUp(self):
        """Set up test data."""
        # Create technology domain
        self.domain = TechnologyDomain.objects.create(code='CHEM')
        self.domain.set_current_language('en')
        self.domain.name = 'Chemistry'
        self.domain.save()

        # Create parent category
        self.parent_category = InfrastructureCategory.objects.create(
            code='ANAL',
            technology_domain=self.domain,
            is_active=True
        )
        self.parent_category.set_current_language('en')
        self.parent_category.name = 'Analytical Labs'
        self.parent_category.save()

        # Create child category
        self.child_category = InfrastructureCategory.objects.create(
            code='ANAL-SPEC',
            technology_domain=self.domain,
            parent=self.parent_category,
            is_active=True
        )
        self.child_category.set_current_language('en')
        self.child_category.name = 'Spectroscopy Labs'
        self.child_category.save()

    def test_infrastructure_category_creation(self):
        """Test infrastructure category is created correctly."""
        self.assertEqual(self.parent_category.code, 'ANAL')
        self.assertEqual(self.parent_category.technology_domain, self.domain)
        self.assertEqual(InfrastructureCategory.objects.count(), 2)

    def test_infrastructure_category_str_representation(self):
        """Test infrastructure category string representation."""
        self.assertIn('ANAL', str(self.parent_category))
        self.assertIn('Analytical Labs', str(self.parent_category))

    def test_infrastructure_category_hierarchy(self):
        """Test hierarchical relationship."""
        self.assertEqual(self.child_category.parent, self.parent_category)
        self.assertIn(self.child_category, self.parent_category.subcategories.all())

    def test_infrastructure_category_level_property(self):
        """Test level property."""
        self.assertEqual(self.parent_category.level, 0)
        self.assertEqual(self.child_category.level, 1)


class TagModelTest(TestCase):
    """Tests for Tag model."""

    def setUp(self):
        """Set up test data."""
        self.tag = Tag.objects.create(
            slug='nanomaterials',
            tag_type='material',
            color='#FF6B6B',
            is_active=True,
            usage_count=0
        )
        self.tag.set_current_language('en')
        self.tag.name = 'Nanomaterials'
        self.tag.description = 'Materials at nanoscale'
        self.tag.save()

    def test_tag_creation(self):
        """Test tag is created correctly."""
        self.assertEqual(self.tag.slug, 'nanomaterials')
        self.assertEqual(self.tag.tag_type, 'material')
        self.assertEqual(self.tag.color, '#FF6B6B')
        self.assertEqual(self.tag.usage_count, 0)
        self.assertEqual(Tag.objects.count(), 1)

    def test_tag_str_representation(self):
        """Test tag string representation."""
        self.assertEqual(str(self.tag), 'Nanomaterials')

    def test_tag_increment_usage(self):
        """Test increment_usage method."""
        initial_count = self.tag.usage_count
        self.tag.increment_usage()
        self.assertEqual(self.tag.usage_count, initial_count + 1)

    def test_tag_auto_slug_generation(self):
        """Test automatic slug generation."""
        tag = Tag(tag_type='technique', is_active=True)
        tag.set_current_language('en')
        tag.name = 'Electron Microscopy'
        tag.save()

        self.assertEqual(tag.slug, 'electron-microscopy')

    def test_tag_slug_unique(self):
        """Test slug must be unique."""
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Tag.objects.create(
                slug='nanomaterials',
                tag_type='technique'
            )
