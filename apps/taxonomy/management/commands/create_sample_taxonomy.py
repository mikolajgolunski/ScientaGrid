from django.core.management.base import BaseCommand
from apps.taxonomy.models import TechnologyDomain, InfrastructureCategory, Tag
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment
from apps.services.models import Service


class Command(BaseCommand):
    help = 'Creates sample taxonomy data'

    def handle(self, *args, **options):
        # Create Technology Domains
        # Top-level domains
        physics, _ = TechnologyDomain.objects.get_or_create(
            code='PHYS',
            defaults={'is_active': True}
        )
        physics.set_current_language('en')
        physics.name = 'Physics'
        physics.description = 'Physical sciences and related technologies'
        physics.set_current_language('pl')
        physics.name = 'Fizyka'
        physics.description = 'Nauki fizyczne i technologie pokrewne'
        physics.save()

        chemistry, _ = TechnologyDomain.objects.get_or_create(
            code='CHEM',
            defaults={'is_active': True}
        )
        chemistry.set_current_language('en')
        chemistry.name = 'Chemistry'
        chemistry.description = 'Chemical sciences and analytical techniques'
        chemistry.set_current_language('pl')
        chemistry.name = 'Chemia'
        chemistry.description = 'Nauki chemiczne i techniki analityczne'
        chemistry.save()

        biology, _ = TechnologyDomain.objects.get_or_create(
            code='BIO',
            defaults={'is_active': True}
        )
        biology.set_current_language('en')
        biology.name = 'Biology & Life Sciences'
        biology.description = 'Biological and life science technologies'
        biology.set_current_language('pl')
        biology.name = 'Biologia i Nauki o Życiu'
        biology.description = 'Technologie biologiczne i nauk o życiu'
        biology.save()

        materials, _ = TechnologyDomain.objects.get_or_create(
            code='MAT',
            defaults={'is_active': True}
        )
        materials.set_current_language('en')
        materials.name = 'Materials Science'
        materials.description = 'Material characterization and engineering'
        materials.set_current_language('pl')
        materials.name = 'Nauka o Materiałach'
        materials.description = 'Charakteryzacja i inżynieria materiałowa'
        materials.save()

        # Sub-domains
        nanoscience, _ = TechnologyDomain.objects.get_or_create(
            code='PHYS-NANO',
            defaults={'parent': physics, 'is_active': True}
        )
        nanoscience.set_current_language('en')
        nanoscience.name = 'Nanoscience & Nanotechnology'
        nanoscience.description = 'Nanoscale research and applications'
        nanoscience.set_current_language('pl')
        nanoscience.name = 'Nanonauka i Nanotechnologia'
        nanoscience.description = 'Badania i aplikacje w nanoskali'
        nanoscience.save()

        spectroscopy, _ = TechnologyDomain.objects.get_or_create(
            code='CHEM-SPEC',
            defaults={'parent': chemistry, 'is_active': True}
        )
        spectroscopy.set_current_language('en')
        spectroscopy.name = 'Spectroscopy'
        spectroscopy.description = 'Spectroscopic analysis techniques'
        spectroscopy.set_current_language('pl')
        spectroscopy.name = 'Spektroskopia'
        spectroscopy.description = 'Techniki analizy spektroskopowej'
        spectroscopy.save()

        self.stdout.write(self.style.SUCCESS('Created technology domains'))

        # Create Infrastructure Categories
        microscopy, _ = InfrastructureCategory.objects.get_or_create(
            code='MICRO',
            defaults={
                'technology_domain': physics,
                'is_active': True
            }
        )
        microscopy.set_current_language('en')
        microscopy.name = 'Microscopy Facilities'
        microscopy.description = 'Facilities for microscopic imaging and analysis'
        microscopy.set_current_language('pl')
        microscopy.name = 'Laboratoria Mikroskopii'
        microscopy.description = 'Obiekty do obrazowania i analizy mikroskopowej'
        microscopy.save()

        analytical, _ = InfrastructureCategory.objects.get_or_create(
            code='ANAL',
            defaults={
                'technology_domain': chemistry,
                'is_active': True
            }
        )
        analytical.set_current_language('en')
        analytical.name = 'Analytical Laboratories'
        analytical.description = 'Chemical and physical analysis facilities'
        analytical.set_current_language('pl')
        analytical.name = 'Laboratoria Analityczne'
        analytical.description = 'Obiekty do analiz chemicznych i fizycznych'
        analytical.save()

        # Sub-category
        electron_micro, _ = InfrastructureCategory.objects.get_or_create(
            code='MICRO-EM',
            defaults={
                'parent': microscopy,
                'technology_domain': nanoscience,
                'is_active': True
            }
        )
        electron_micro.set_current_language('en')
        electron_micro.name = 'Electron Microscopy'
        electron_micro.description = 'Electron microscopy facilities (TEM, SEM, etc.)'
        electron_micro.set_current_language('pl')
        electron_micro.name = 'Mikroskopia Elektronowa'
        electron_micro.description = 'Laboratoria mikroskopii elektronowej (TEM, SEM, itp.)'
        electron_micro.save()

        self.stdout.write(self.style.SUCCESS('Created infrastructure categories'))

        # Create Tags
        tags_data = [
            ('nanomaterials', 'Nanomaterials', 'technique', '#FF6B6B'),
            ('characterization', 'Characterization', 'application', '#4ECDC4'),
            ('imaging', 'Imaging', 'technique', '#45B7D1'),
            ('crystallography', 'Crystallography', 'discipline', '#96CEB4'),
            ('surface-analysis', 'Surface Analysis', 'application', '#FFEAA7'),
            ('polymer', 'Polymer Science', 'material', '#DFE6E9'),
            ('biomedical', 'Biomedical Applications', 'application', '#74B9FF'),
            ('environmental', 'Environmental Science', 'discipline', '#55EFC4'),
        ]

        created_tags = []
        for slug, name_en, tag_type, color in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=slug,
                defaults={
                    'tag_type': tag_type,
                    'color': color,
                    'is_active': True
                }
            )
            if created:
                tag.set_current_language('en')
                tag.name = name_en
                tag.set_current_language('pl')
                # Simple Polish translations (you can improve these)
                tag.name = name_en  # Keep English for now, you can add Polish later
                tag.save()
                created_tags.append(tag)

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_tags)} tags'))

        # Link taxonomy to existing data
        infrastructures = Infrastructure.objects.all()
        if infrastructures.exists():
            infra = infrastructures.first()
            infra.technology_domains.add(physics, nanoscience)
            infra.categories.add(microscopy, electron_micro)
            infra.tags.add(*Tag.objects.filter(slug__in=['imaging', 'nanomaterials', 'characterization'])[:3])
            self.stdout.write(self.style.SUCCESS('Linked taxonomy to infrastructure'))

        equipment = Equipment.objects.all()
        if equipment.exists():
            eq = equipment.first()
            eq.technology_domains.add(nanoscience)
            eq.tags.add(*Tag.objects.filter(slug__in=['imaging', 'nanomaterials'])[:2])
            self.stdout.write(self.style.SUCCESS('Linked taxonomy to equipment'))

        services = Service.objects.all()
        if services.exists():
            svc = services.first()
            svc.technology_domains.add(physics, nanoscience)
            svc.tags.add(*Tag.objects.filter(slug__in=['imaging', 'characterization'])[:2])
            self.stdout.write(self.style.SUCCESS('Linked taxonomy to services'))

        self.stdout.write(self.style.SUCCESS('Sample taxonomy setup complete!'))