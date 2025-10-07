from django.test import TestCase
from decimal import Decimal
from apps.research_problems.models import FieldOfScience, Keyword, ResearchProblem


class FieldOfScienceModelTest(TestCase):
    """Tests for FieldOfScience model."""

    def setUp(self):
        """Set up test data."""
        # Create parent field
        self.parent_field = FieldOfScience.objects.create(
            code='1',
            is_active=True
        )
        self.parent_field.set_current_language('en')
        self.parent_field.name = 'Natural Sciences'
        self.parent_field.description = 'Physical and life sciences'
        self.parent_field.save()

        # Create child field
        self.child_field = FieldOfScience.objects.create(
            code='1.3',
            parent=self.parent_field,
            is_active=True
        )
        self.child_field.set_current_language('en')
        self.child_field.name = 'Physical Sciences'
        self.child_field.save()

    def test_field_of_science_creation(self):
        """Test field of science is created correctly."""
        self.assertEqual(self.parent_field.code, '1')
        self.assertTrue(self.parent_field.is_active)
        self.assertEqual(FieldOfScience.objects.count(), 2)

    def test_field_of_science_str_representation(self):
        """Test field of science string representation."""
        self.assertIn('1', str(self.parent_field))
        self.assertIn('Natural Sciences', str(self.parent_field))

    def test_field_of_science_hierarchy(self):
        """Test hierarchical relationship."""
        self.assertEqual(self.child_field.parent, self.parent_field)
        self.assertIn(self.child_field, self.parent_field.subfields.all())

    def test_field_of_science_level_property(self):
        """Test level property."""
        self.assertEqual(self.parent_field.level, 0)
        self.assertEqual(self.child_field.level, 1)

    def test_field_of_science_full_path_property(self):
        """Test full_path property."""
        self.assertEqual(self.parent_field.full_path, 'Natural Sciences')
        self.assertIn('Natural Sciences', self.child_field.full_path)
        self.assertIn('Physical Sciences', self.child_field.full_path)


class KeywordModelTest(TestCase):
    """Tests for Keyword model."""

    def setUp(self):
        """Set up test data."""
        # Create field of science
        self.field = FieldOfScience.objects.create(code='1.3')
        self.field.set_current_language('en')
        self.field.name = 'Physical Sciences'
        self.field.save()

        # Create keyword
        self.keyword = Keyword.objects.create(
            slug='nanomaterials',
            field_of_science=self.field,
            is_active=True,
            usage_count=0
        )
        self.keyword.set_current_language('en')
        self.keyword.name = 'Nanomaterials'
        self.keyword.description = 'Materials at nanoscale'
        self.keyword.save()

    def test_keyword_creation(self):
        """Test keyword is created correctly."""
        self.assertEqual(self.keyword.slug, 'nanomaterials')
        self.assertEqual(self.keyword.field_of_science, self.field)
        self.assertEqual(self.keyword.usage_count, 0)
        self.assertEqual(Keyword.objects.count(), 1)

    def test_keyword_str_representation(self):
        """Test keyword string representation."""
        self.assertEqual(str(self.keyword), 'Nanomaterials')

    def test_keyword_increment_usage(self):
        """Test increment_usage method."""
        initial_count = self.keyword.usage_count
        self.keyword.increment_usage()
        self.assertEqual(self.keyword.usage_count, initial_count + 1)

    def test_keyword_auto_slug_generation(self):
        """Test automatic slug generation."""
        kw = Keyword(field_of_science=self.field, is_active=True)
        kw.set_current_language('en')
        kw.name = 'Electron Microscopy'
        kw.save()

        self.assertEqual(kw.slug, 'electron-microscopy')


class ResearchProblemModelTest(TestCase):
    """Tests for ResearchProblem model."""

    def setUp(self):
        """Set up test data."""
        # Create field of science
        self.field = FieldOfScience.objects.create(code='2.10')
        self.field.set_current_language('en')
        self.field.name = 'Nanotechnology'
        self.field.save()

        # Create keywords
        self.keyword1 = Keyword.objects.create(slug='nanoparticles')
        self.keyword1.set_current_language('en')
        self.keyword1.name = 'Nanoparticles'
        self.keyword1.save()

        self.keyword2 = Keyword.objects.create(slug='characterization')
        self.keyword2.set_current_language('en')
        self.keyword2.name = 'Characterization'
        self.keyword2.save()

        # Create research problem
        self.problem = ResearchProblem.objects.create(
            field_of_science=self.field,
            complexity=4,
            priority='high',
            status='active',
            estimated_budget=Decimal('5000.00'),
            estimated_duration_days=30,
            is_public=True,
            submitted_by='Dr. Test Researcher',
            contact_email='researcher@example.com'
        )
        self.problem.set_current_language('en')
        self.problem.title = 'Nanoparticle Characterization Study'
        self.problem.description = 'Comprehensive characterization of gold nanoparticles'
        self.problem.required_capabilities = 'TEM imaging, spectroscopy'
        self.problem.expected_outcomes = 'Size distribution, morphology analysis'
        self.problem.constraints = 'Budget limited, tight deadline'
        self.problem.save()

        self.problem.keywords.add(self.keyword1, self.keyword2)

    def test_research_problem_creation(self):
        """Test research problem is created correctly."""
        self.assertEqual(self.problem.field_of_science, self.field)
        self.assertEqual(self.problem.complexity, 4)
        self.assertEqual(self.problem.priority, 'high')
        self.assertEqual(self.problem.status, 'active')
        self.assertTrue(self.problem.is_public)
        self.assertEqual(ResearchProblem.objects.count(), 1)

    def test_research_problem_str_representation(self):
        """Test research problem string representation."""
        self.assertEqual(str(self.problem), 'Nanoparticle Characterization Study')

    def test_research_problem_keywords(self):
        """Test research problem keywords relationship."""
        self.assertEqual(self.problem.keywords.count(), 2)
        self.assertIn(self.keyword1, self.problem.keywords.all())
        self.assertIn(self.keyword2, self.problem.keywords.all())

    def test_research_problem_get_all_fields(self):
        """Test get_all_fields method."""
        # Add additional field
        additional_field = FieldOfScience.objects.create(code='1.4')
        additional_field.set_current_language('en')
        additional_field.name = 'Chemical Sciences'
        additional_field.save()

        self.problem.additional_fields.add(additional_field)

        fields = self.problem.get_all_fields()
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0], self.field)  # Primary field is first
        self.assertIn(additional_field, fields)

    def test_research_problem_complexity_choices(self):
        """Test complexity is within valid range."""
        self.assertIn(self.problem.complexity, [1, 2, 3, 4, 5])

    def test_research_problem_priority_choices(self):
        """Test priority is one of valid choices."""
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        self.assertIn(self.problem.priority, valid_priorities)

    def test_research_problem_status_choices(self):
        """Test status is one of valid choices."""
        valid_statuses = ['draft', 'active', 'matched', 'in_progress', 'completed', 'on_hold', 'cancelled']
        self.assertIn(self.problem.status, valid_statuses)