from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields


class TechnologyDomain(TranslatableModel):
    """Represents broad technology domains for classification."""

    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        description=models.TextField(blank=True)
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for this domain"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subdomains',
        help_text="Parent domain for hierarchical structure"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name_plural = "Technology Domains"

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or f"Domain {self.id}"
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


class InfrastructureCategory(TranslatableModel):
    """Represents categories for infrastructures."""

    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        description=models.TextField(blank=True)
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for this category"
    )

    technology_domain = models.ForeignKey(
        TechnologyDomain,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='infrastructure_categories',
        help_text="Related technology domain"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text="Parent category for hierarchical structure"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name_plural = "Infrastructure Categories"

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or f"Category {self.id}"
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


class Tag(TranslatableModel):
    """Represents flexible tags for categorization across the system."""

    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        description=models.TextField(blank=True)
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly version of the tag name"
    )

    TAG_TYPES = [
        ('general', 'General'),
        ('technique', 'Technique'),
        ('material', 'Material'),
        ('application', 'Application'),
        ('discipline', 'Discipline'),
        ('custom', 'Custom'),
    ]
    tag_type = models.CharField(
        max_length=20,
        choices=TAG_TYPES,
        default='general',
        help_text="Type of tag for filtering and organization"
    )

    color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex color code for visual representation (e.g., #FF5733)"
    )

    is_active = models.BooleanField(default=True)

    usage_count = models.IntegerField(
        default=0,
        help_text="Number of times this tag has been used"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tag_type', 'translations__name']

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or self.slug

    def increment_usage(self):
        """Increment usage count."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug and self.has_translation():
            # Get the current language name for slug generation
            current_name = self.safe_translation_getter('name', any_language=True)
            if current_name:
                base_slug = slugify(current_name)
                slug = base_slug
                counter = 1
                # Ensure slug is unique
                while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug
        super().save(*args, **kwargs)
