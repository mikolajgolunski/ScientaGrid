from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class FieldOfScience(TranslatableModel):
    """Represents scientific fields and disciplines for classification."""

    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        description=models.TextField(blank=True)
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for this field (e.g., OECD FOS code)"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subfields',
        help_text="Parent field for hierarchical structure"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name_plural = "Fields of Science"

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or f"Field {self.id}"
        if self.code:
            return f"{self.code}: {name}"
        return name

    @property
    def full_path(self):
        """Get full hierarchical path."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

    @property
    def level(self):
        """Get hierarchy level (0 for top-level)."""
        if self.parent:
            return self.parent.level + 1
        return 0


class Keyword(TranslatableModel):
    """Represents keywords for tagging and searching research problems."""

    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        description=models.TextField(blank=True)
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly version of the keyword"
    )

    field_of_science = models.ForeignKey(
        FieldOfScience,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='keywords',
        help_text="Primary field of science this keyword relates to"
    )

    is_active = models.BooleanField(default=True)

    usage_count = models.IntegerField(
        default=0,
        help_text="Number of times this keyword has been used"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or self.slug

    def increment_usage(self):
        """Increment usage count."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug and self.has_translation():
            from django.utils.text import slugify
            current_name = self.safe_translation_getter('name', any_language=True)
            if current_name:
                base_slug = slugify(current_name)
                slug = base_slug
                counter = 1
                # Ensure slug is unique
                while Keyword.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug
        super().save(*args, **kwargs)


class ResearchProblem(TranslatableModel):
    """Represents a research problem or need that can be matched to infrastructures."""

    translations = TranslatedFields(
        title=models.CharField(max_length=255),
        description=models.TextField(
            help_text="Detailed description of the research problem"
        ),
        required_capabilities=models.TextField(
            blank=True,
            help_text="Specific capabilities or techniques needed"
        ),
        expected_outcomes=models.TextField(
            blank=True,
            help_text="What the researcher expects to achieve"
        ),
        constraints=models.TextField(
            blank=True,
            help_text="Any constraints or limitations (budget, time, sample type, etc.)"
        )
    )

    # Classification
    field_of_science = models.ForeignKey(
        FieldOfScience,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='research_problems',
        help_text="Primary field of science for this problem"
    )

    additional_fields = models.ManyToManyField(
        FieldOfScience,
        blank=True,
        related_name='additional_research_problems',
        help_text="Additional relevant fields of science"
    )

    keywords = models.ManyToManyField(
        Keyword,
        blank=True,
        related_name='research_problems',
        help_text="Keywords describing this research problem"
    )

    # Problem characteristics
    COMPLEXITY_LEVELS = [
        (1, 'Very Simple'),
        (2, 'Simple'),
        (3, 'Moderate'),
        (4, 'Complex'),
        (5, 'Very Complex'),
    ]
    complexity = models.IntegerField(
        choices=COMPLEXITY_LEVELS,
        default=3,
        help_text="Estimated complexity of the research problem"
    )

    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        help_text="Priority level for solving this problem"
    )

    # Budget and timeline
    estimated_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated budget in PLN"
    )

    estimated_duration_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Estimated duration to complete in days"
    )

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('matched', 'Matched to Infrastructure'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # Tracking
    is_public = models.BooleanField(
        default=False,
        help_text="Can this problem be publicly visible?"
    )

    submitted_by = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name or organization that submitted this problem"
    )

    contact_email = models.EmailField(
        blank=True,
        help_text="Contact email for this research problem"
    )

    internal_notes = models.TextField(
        blank=True,
        help_text="Internal staff notes about this problem"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or f"Research Problem {self.id}"

    def get_all_fields(self):
        """Get all related fields of science."""
        fields = list(self.additional_fields.all())
        if self.field_of_science:
            fields.insert(0, self.field_of_science)
        return fields


# Add many-to-many relationship to Infrastructure for matched problems
from apps.infrastructures.models import Infrastructure

Infrastructure.add_to_class(
    'research_problems',
    models.ManyToManyField(
        ResearchProblem,
        blank=True,
        related_name='matched_infrastructures',
        help_text="Research problems this infrastructure can help solve"
    )
)