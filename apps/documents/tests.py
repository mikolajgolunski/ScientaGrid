from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.documents.models import DocumentType, Document
from apps.infrastructures.models import Infrastructure
from apps.institutions.models import Institution
from apps.locations.models import Country, Region, City
from apps.users.models import UserProfile, StaffRole


class DocumentTypeModelTest(TestCase):
    """Tests for DocumentType model."""

    def setUp(self):
        """Set up test data."""
        self.doc_type = DocumentType.objects.create(
            code='MANUAL',
            allowed_extensions='pdf,doc,docx',
            max_file_size_mb=50,
            icon='book',
            is_active=True
        )
        self.doc_type.set_current_language('en')
        self.doc_type.name = 'User Manual'
        self.doc_type.description = 'Equipment user manuals'
        self.doc_type.save()

    def test_document_type_creation(self):
        """Test document type is created correctly."""
        self.assertEqual(self.doc_type.code, 'MANUAL')
        self.assertEqual(self.doc_type.max_file_size_mb, 50)
        self.assertTrue(self.doc_type.is_active)
        self.assertEqual(DocumentType.objects.count(), 1)

    def test_document_type_str_representation(self):
        """Test document type string representation."""
        self.assertIn('MANUAL', str(self.doc_type))
        self.assertIn('User Manual', str(self.doc_type))

    def test_document_type_get_allowed_extensions_list(self):
        """Test get_allowed_extensions_list method."""
        extensions = self.doc_type.get_allowed_extensions_list()
        self.assertEqual(len(extensions), 3)
        self.assertIn('pdf', extensions)
        self.assertIn('doc', extensions)
        self.assertIn('docx', extensions)


class DocumentModelTest(TestCase):
    """Tests for Document model."""

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

        # Create location hierarchy
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

        # Create document type
        self.doc_type = DocumentType.objects.create(
            code='MANUAL',
            allowed_extensions='pdf',
            max_file_size_mb=10
        )
        self.doc_type.set_current_language('en')
        self.doc_type.name = 'Manual'
        self.doc_type.save()

        # Create test file
        test_file = SimpleUploadedFile(
            "test_manual.pdf",
            b"file_content",
            content_type="application/pdf"
        )

        # Create document
        self.document = Document.objects.create(
            infrastructure=self.infrastructure,
            document_type=self.doc_type,
            file=test_file,
            version='1.0',
            status='active',
            is_public=False,
            requires_login=True,
            uploaded_by=self.user
        )
        self.document.set_current_language('en')
        self.document.title = 'Equipment Manual'
        self.document.description = 'User manual for test equipment'
        self.document.save()

    def test_document_creation(self):
        """Test document is created correctly."""
        self.assertEqual(self.document.infrastructure, self.infrastructure)
        self.assertEqual(self.document.document_type, self.doc_type)
        self.assertEqual(self.document.version, '1.0')
        self.assertEqual(self.document.status, 'active')
        self.assertEqual(Document.objects.count(), 1)

    def test_document_str_representation(self):
        """Test document string representation."""
        self.assertEqual(str(self.document), 'Equipment Manual')

    def test_document_filename_property(self):
        """Test filename property."""
        self.assertIn('test_manual.pdf', self.document.filename)

    def test_document_file_size_mb_property(self):
        """Test file_size_mb property."""
        file_size_mb = self.document.file_size_mb
        self.assertIsInstance(file_size_mb, (int, float))
        self.assertGreaterEqual(file_size_mb, 0)

    def test_document_get_related_object(self):
        """Test get_related_object method."""
        related_obj = self.document.get_related_object()
        self.assertEqual(related_obj, self.infrastructure)

    def test_document_increment_download_count(self):
        """Test increment_download_count method."""
        initial_count = self.document.download_count
        self.document.increment_download_count()

        self.assertEqual(self.document.download_count, initial_count + 1)
        self.assertIsNotNone(self.document.last_downloaded_at)

    def test_document_validation_requires_object(self):
        """Test document must be linked to at least one object."""
        doc = Document(
            document_type=self.doc_type,
            file=SimpleUploadedFile("test.pdf", b"content"),
            uploaded_by=self.user
        )
        doc.set_current_language('en')
        doc.title = 'Invalid Document'

        with self.assertRaises(ValidationError):
            doc.full_clean()

    def test_document_file_metadata_auto_population(self):
        """Test file metadata is automatically populated."""
        self.assertIsNotNone(self.document.file_size)
        self.assertEqual(self.document.file_extension, 'pdf')
        self.assertEqual(self.document.mime_type, 'application/pdf')
