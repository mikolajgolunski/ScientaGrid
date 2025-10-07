from django.db import models
from apps.users.models import UserProfile
import json


class SavedSearch(models.Model):
    """Allows users to save their search queries for later use."""

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )

    name = models.CharField(
        max_length=200,
        help_text="Name for this saved search"
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of what this search is for"
    )

    # Search parameters stored as JSON
    search_params = models.JSONField(
        help_text="JSON representation of search parameters"
    )

    # What type of search
    SEARCH_TYPES = [
        ('infrastructure', 'Infrastructure Search'),
        ('equipment', 'Equipment Search'),
        ('service', 'Service Search'),
        ('research_problem', 'Research Problem Search'),
        ('mixed', 'Mixed Search'),
    ]
    search_type = models.CharField(
        max_length=20,
        choices=SEARCH_TYPES,
        default='infrastructure'
    )

    # Usage tracking
    usage_count = models.IntegerField(
        default=0,
        help_text="Number of times this search has been used"
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this search was executed"
    )

    # Notifications
    notify_on_new_results = models.BooleanField(
        default=False,
        help_text="Send notification when new results match this search"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_used_at', '-created_at']
        verbose_name_plural = "Saved Searches"

    def __str__(self):
        return f"{self.user.username}: {self.name}"

    def increment_usage(self):
        """Increment usage counter and update last used timestamp."""
        from django.utils import timezone
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])

    def get_params_dict(self):
        """Get search parameters as dictionary."""
        return self.search_params if isinstance(self.search_params, dict) else {}


class SearchLog(models.Model):
    """Logs search queries for analytics and improvement."""

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_logs'
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Search query
    query_text = models.CharField(
        max_length=500,
        blank=True,
        help_text="Free text search query"
    )

    filters = models.JSONField(
        default=dict,
        help_text="Applied filters as JSON"
    )

    # Search type
    SEARCH_TYPES = [
        ('infrastructure', 'Infrastructure Search'),
        ('equipment', 'Equipment Search'),
        ('service', 'Service Search'),
        ('research_problem', 'Research Problem Search'),
        ('mixed', 'Mixed Search'),
    ]
    search_type = models.CharField(
        max_length=20,
        choices=SEARCH_TYPES,
        default='infrastructure'
    )

    # Results
    results_count = models.IntegerField(
        default=0,
        help_text="Number of results returned"
    )

    execution_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Search execution time in milliseconds"
    )

    # User interaction
    clicked_result_ids = models.JSONField(
        default=list,
        help_text="IDs of results that were clicked"
    )

    session_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Session identifier for grouping searches"
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['search_type', '-timestamp']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{user_str} searched '{self.query_text}' at {self.timestamp}"