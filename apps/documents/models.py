from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment
from apps.services.models import Service
import os


class DocumentType(TranslatableModel):
    """Represents types/categories of documents."""

    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        description=models.TextField(blank=True)
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for this document type"
    )

    # File type restrictions
    allowed_extensions = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated list of allowed file extensions (e.g., pdf,doc,docx)"
    )

    max_file_size_mb = models.IntegerField(
        default=10,
        help_text="Maximum file size in megabytes"
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon name or class for UI display"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        name = self.safe_translation_getter('name', any_language=True) or f"Document Type {self.id}"
        return f"{self.code}: {name}"

    def get_allowed_extensions_list(self):
        """Parse allowed extensions string into a list."""
        if self.allowed_extensions:
            return [ext.strip().lower() for ext in self.allowed_extensions.split(',')]
        return []


def document_upload_path(instance, filename):
    """Generate upload path for documents."""
    # Get the type of related object
    if instance.infrastructure:
        folder = f'infrastructures/{instance.infrastructure.id}'
    elif instance.equipment:
        folder = f'equipment/{instance.equipment.id}'
    elif instance.service:
        folder = f'services/{instance.service.id}'
    else:
        folder = 'general'

    # Add document type subfolder
    if instance.document_type:
        folder = f'{folder}/{instance.document_type.code}'

    return f'documents/{folder}/{filename}'


class Document(TranslatableModel):
    """Represents a document/file attachment."""

    translations = TranslatedFields(
        title=models.CharField(max_length=255),
        description=models.TextField(blank=True)
    )

    # File
    file = models.FileField(
        upload_to=document_upload_path,
        help_text="Upload the document file"
    )

    # What this document relates to
    infrastructure = models.ForeignKey(
        Infrastructure,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )

    # Document classification
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )

    # File metadata
    file_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )

    file_extension = models.CharField(
        max_length=10,
        blank=True,
        help_text="File extension (automatically detected)"
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="MIME type of the file"
    )

    # Versioning
    version = models.CharField(
        max_length=20,
        default='1.0',
        help_text="Document version number"
    )

    replaces = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replaced_by_documents',
        help_text="Previous version of this document"
    )

    # Visibility and access
    is_public = models.BooleanField(
        default=False,
        help_text="Is this document publicly accessible?"
    )

    requires_login = models.BooleanField(
        default=True,
        help_text="Does viewing this document require login?"
    )

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('obsolete', 'Obsolete'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    # Tracking
    uploaded_by = models.ForeignKey(
        'users.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )

    download_count = models.IntegerField(
        default=0,
        help_text="Number of times this document has been downloaded"
    )

    last_downloaded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this document was downloaded"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        title = self.safe_translation_getter('title', any_language=True) or self.filename
        return title

    @property
    def filename(self):
        """Get the filename from the file path."""
        if self.file:
            return os.path.basename(self.file.name)
        return ''

    @property
    def file_size_mb(self):
        """Get file size in megabytes."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0

    def get_related_object(self):
        """Get the object this document is related to."""
        if self.infrastructure:
            return self.infrastructure
        elif self.equipment:
            return self.equipment
        elif self.service:
            return self.service
        return None

    def increment_download_count(self):
        """Increment download counter."""
        from django.utils import timezone
        self.download_count += 1
        self.last_downloaded_at = timezone.now()
        self.save(update_fields=['download_count', 'last_downloaded_at'])

    def save(self, *args, **kwargs):
        """Auto-populate file metadata on save."""
        if self.file:
            # Get file size
            if not self.file_size:
                self.file_size = self.file.size

            # Get file extension
            if not self.file_extension:
                _, ext = os.path.splitext(self.file.name)
                self.file_extension = ext.lower().replace('.', '')

            # Get MIME type (basic detection)
            if not self.mime_type:
                ext_mime_map = {
                    'pdf': 'application/pdf',
                    'doc': 'application/msword',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'xls': 'application/vnd.ms-excel',
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'ppt': 'application/vnd.ms-powerpoint',
                    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'txt': 'text/plain',
                    'csv': 'text/csv',
                }
                self.mime_type = ext_mime_map.get(self.file_extension, 'application/octet-stream')

        super().save(*args, **kwargs)

    def clean(self):
        """Validate document."""
        from django.core.exceptions import ValidationError

        # Ensure at least one relationship is set
        if not any([self.infrastructure, self.equipment, self.service]):
            raise ValidationError(
                'Document must be linked to at least one: infrastructure, equipment, or service'
            )

        # Validate file extension if document type has restrictions
        if self.document_type and self.document_type.allowed_extensions and self.file:
            allowed = self.document_type.get_allowed_extensions_list()
            if allowed and self.file_extension not in allowed:
                raise ValidationError(
                    f"File type '.{self.file_extension}' is not allowed for this document type. "
                    f"Allowed types: {', '.join(allowed)}"
                )

        # Validate file size
        if self.document_type and self.file_size:
            max_size = self.document_type.max_file_size_mb * 1024 * 1024
            if self.file_size > max_size:
                raise ValidationError(
                    f"File size ({self.file_size_mb} MB) exceeds maximum allowed "
                    f"({self.document_type.max_file_size_mb} MB)"
                )