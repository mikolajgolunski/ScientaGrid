from django.core.management.base import BaseCommand
from apps.services.models import Service, EquipmentService
from apps.equipment.models import Equipment


class Command(BaseCommand):
    help = 'Creates sample services and links them to equipment'

    def handle(self, *args, **options):
        # Get equipment
        equipment = Equipment.objects.all()

        if not equipment.exists():
            self.stdout.write(self.style.ERROR(
                'No equipment found. Run create_sample_equipment first.'
            ))
            return

        # Create service 1: Electron Microscopy Imaging
        service1, created = Service.objects.get_or_create(
            code='TEM-IMG',
            defaults={
                'typical_turnaround_days': 7,
                'is_active': True
            }
        )
        if created:
            service1.set_current_language('en')
            service1.name = 'Transmission Electron Microscopy Imaging'
            service1.description = 'High-resolution imaging at nanoscale using TEM'
            service1.methodology = 'Sample preparation, TEM imaging, image analysis'
            service1.typical_applications = 'Nanomaterial characterization, biological samples, crystal structure analysis'
            service1.deliverables = 'High-resolution TEM images (TIFF format), measurement data, analysis report'
            service1.set_current_language('pl')
            service1.name = 'Obrazowanie Transmisyjną Mikroskopią Elektronową'
            service1.description = 'Obrazowanie wysokiej rozdzielczości w nanoskali przy użyciu TEM'
            service1.methodology = 'Przygotowanie próbek, obrazowanie TEM, analiza obrazu'
            service1.typical_applications = 'Charakteryzacja nanomateriałów, próbki biologiczne, analiza struktury krystalicznej'
            service1.deliverables = 'Obrazy TEM wysokiej rozdzielczości (format TIFF), dane pomiarowe, raport analizy'
            service1.save()
            self.stdout.write(self.style.SUCCESS('Created TEM Imaging service'))
        else:
            self.stdout.write('TEM Imaging service already exists')

        # Create service 2: UV-Vis Spectroscopy
        service2, created = Service.objects.get_or_create(
            code='UVVIS-SPEC',
            defaults={
                'typical_turnaround_days': 2,
                'is_active': True
            }
        )
        if created:
            service2.set_current_language('en')
            service2.name = 'UV-Vis Spectroscopy Analysis'
            service2.description = 'Absorbance and transmittance measurements in UV-Vis range'
            service2.methodology = 'Sample measurement using double-beam spectrophotometer'
            service2.typical_applications = 'Concentration determination, kinetic studies, material characterization'
            service2.deliverables = 'Spectral data (CSV/Excel), absorption spectra graphs, analysis report'
            service2.set_current_language('pl')
            service2.name = 'Analiza Spektroskopii UV-Vis'
            service2.description = 'Pomiary absorbancji i transmitancji w zakresie UV-Vis'
            service2.methodology = 'Pomiar próbki za pomocą dwuwiązkowego spektrofotometru'
            service2.typical_applications = 'Oznaczanie stężenia, badania kinetyczne, charakteryzacja materiałów'
            service2.deliverables = 'Dane spektralne (CSV/Excel), wykresy widm absorpcji, raport analizy'
            service2.save()
            self.stdout.write(self.style.SUCCESS('Created UV-Vis Spectroscopy service'))
        else:
            self.stdout.write('UV-Vis Spectroscopy service already exists')

        # Create service 3: X-ray Diffraction
        service3, created = Service.objects.get_or_create(
            code='XRD-ANAL',
            defaults={
                'typical_turnaround_days': 5,
                'is_active': True
            }
        )
        if created:
            service3.set_current_language('en')
            service3.name = 'X-ray Diffraction Analysis'
            service3.description = 'Crystal structure analysis using XRD'
            service3.methodology = 'Sample preparation, XRD measurement, pattern analysis'
            service3.typical_applications = 'Phase identification, crystallinity determination, crystal structure analysis'
            service3.deliverables = 'XRD patterns, phase analysis report, crystallographic data'
            service3.set_current_language('pl')
            service3.name = 'Analiza Dyfrakcji Rentgenowskiej'
            service3.description = 'Analiza struktury krystalicznej przy użyciu XRD'
            service3.methodology = 'Przygotowanie próbki, pomiar XRD, analiza wzorca'
            service3.typical_applications = 'Identyfikacja faz, określanie krystaliczności, analiza struktury krystalicznej'
            service3.deliverables = 'Wzorce XRD, raport analizy fazowej, dane krystalograficzne'
            service3.save()
            self.stdout.write(self.style.SUCCESS('Created XRD Analysis service'))
        else:
            self.stdout.write('XRD Analysis service already exists')

        # Link services to equipment
        # Find TEM equipment
        tem = equipment.filter(model_number='TEM-2100').first()
        if tem:
            link1, created = EquipmentService.objects.get_or_create(
                equipment=tem,
                service=service1,
                defaults={
                    'is_primary': True,
                    'is_available': True,
                    'estimated_cost': 500.00,
                    'capacity_per_day': 4,
                    'notes': 'Requires advance booking, trained operator available'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Linked TEM to TEM Imaging service'))

        # Find Spectrophotometer
        spec = equipment.filter(model_number='UV-2600').first()
        if spec:
            link2, created = EquipmentService.objects.get_or_create(
                equipment=spec,
                service=service2,
                defaults={
                    'is_primary': True,
                    'is_available': True,
                    'estimated_cost': 100.00,
                    'capacity_per_day': 20,
                    'notes': 'Quick turnaround, can be self-operated after brief training'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Linked Spectrophotometer to UV-Vis service'))

        # Find XRD
        xrd = equipment.filter(model_number='XRD-7000').first()
        if xrd:
            link3, created = EquipmentService.objects.get_or_create(
                equipment=xrd,
                service=service3,
                defaults={
                    'is_primary': True,
                    'is_available': False,  # Under maintenance
                    'estimated_cost': 300.00,
                    'capacity_per_day': 6,
                    'notes': 'Currently under maintenance',
                    'specific_limitations': 'Not available until next month'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Linked XRD to XRD Analysis service'))

        self.stdout.write(self.style.SUCCESS('Sample services setup complete!'))