from django.core.management.base import BaseCommand
from apps.documents.models import DocumentType, Document
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment


class Command(BaseCommand):
    help = 'Creates sample document types'

    def handle(self, *args, **options):
        # Create Document Types

        # Manual
        manual, _ = DocumentType.objects.get_or_create(
            code='MANUAL',
            defaults={
                'allowed_extensions': 'pdf,doc,docx',
                'max_file_size_mb': 50,
                'icon': 'book',
                'is_active': True
            }
        )
        manual.set_current_language('en')
        manual.name = 'User Manual'
        manual.description = 'Equipment user manuals and operating instructions'
        manual.set_current_language('pl')
        manual.name = 'Instrukcja Obsługi'
        manual.description = 'Instrukcje obsługi sprzętu i instrukcje operacyjne'
        manual.save()
        self.stdout.write(self.style.SUCCESS('Created Manual document type'))

        # Safety
        safety, _ = DocumentType.objects.get_or_create(
            code='SAFETY',
            defaults={
                'allowed_extensions': 'pdf,doc,docx',
                'max_file_size_mb': 20,
                'icon': 'shield',
                'is_active': True
            }
        )
        safety.set_current_language('en')
        safety.name = 'Safety Protocol'
        safety.description = 'Safety procedures and protocols'
        safety.set_current_language('pl')
        safety.name = 'Protokół Bezpieczeństwa'
        safety.description = 'Procedury i protokoły bezpieczeństwa'
        safety.save()
        self.stdout.write(self.style.SUCCESS('Created Safety document type'))

        # Photo
        photo, _ = DocumentType.objects.get_or_create(
            code='PHOTO',
            defaults={
                'allowed_extensions': 'jpg,jpeg,png,gif',
                'max_file_size_mb': 10,
                'icon': 'camera',
                'is_active': True
            }
        )
        photo.set_current_language('en')
        photo.name = 'Photo'
        photo.description = 'Equipment and facility photographs'
        photo.set_current_language('pl')
        photo.name = 'Zdjęcie'
        photo.description = 'Fotografie sprzętu i obiektów'
        photo.save()
        self.stdout.write(self.style.SUCCESS('Created Photo document type'))

        # Certificate
        certificate, _ = DocumentType.objects.get_or_create(
            code='CERT',
            defaults={
                'allowed_extensions': 'pdf',
                'max_file_size_mb': 10,
                'icon': 'certificate',
                'is_active': True
            }
        )
        certificate.set_current_language('en')
        certificate.name = 'Certificate'
        certificate.description = 'Calibration certificates and certifications'
        certificate.set_current_language('pl')
        certificate.name = 'Certyfikat'
        certificate.description = 'Certyfikaty kalibracji i certyfikacje'
        certificate.save()
        self.stdout.write(self.style.SUCCESS('Created Certificate document type'))

        # Sample Prep
        sample_prep, _ = DocumentType.objects.get_or_create(
            code='SAMPLE',
            defaults={
                'allowed_extensions': 'pdf,doc,docx',
                'max_file_size_mb': 20,
                'icon': 'flask',
                'is_active': True
            }
        )
        sample_prep.set_current_language('en')
        sample_prep.name = 'Sample Preparation Guide'
        sample_prep.description = 'Sample preparation procedures and requirements'
        sample_prep.set_current_language('pl')
        sample_prep.name = 'Przewodnik Przygotowania Próbek'
        sample_prep.description = 'Procedury i wymagania przygotowania próbek'
        sample_prep.save()
        self.stdout.write(self.style.SUCCESS('Created Sample Prep document type'))

        # Technical Spec
        tech_spec, _ = DocumentType.objects.get_or_create(
            code='TECHSPEC',
            defaults={
                'allowed_extensions': 'pdf,doc,docx,xls,xlsx',
                'max_file_size_mb': 30,
                'icon': 'file-text',
                'is_active': True
            }
        )
        tech_spec.set_current_language('en')
        tech_spec.name = 'Technical Specification'
        tech_spec.description = 'Detailed technical specifications and datasheets'
        tech_spec.set_current_language('pl')
        tech_spec.name = 'Specyfikacja Techniczna'
        tech_spec.description = 'Szczegółowe specyfikacje techniczne i karty katalogowe'
        tech_spec.save()
        self.stdout.write(self.style.SUCCESS('Created Technical Spec document type'))

        self.stdout.write(self.style.SUCCESS('Sample document types setup complete!'))
        self.stdout.write(self.style.WARNING(
            'Note: Actual document files need to be uploaded manually through the admin interface.'
        ))