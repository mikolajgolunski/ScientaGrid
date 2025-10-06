from django.core.management.base import BaseCommand
from apps.equipment.models import Equipment
from apps.infrastructures.models import Infrastructure


class Command(BaseCommand):
    help = 'Creates sample equipment'

    def handle(self, *args, **options):
        # Get infrastructures
        infrastructures = Infrastructure.objects.all()

        if not infrastructures.exists():
            self.stdout.write(self.style.ERROR(
                'No infrastructures found. Run create_sample_infrastructures first.'
            ))
            return

        # Get first infrastructure
        infra = infrastructures.first()

        # Create sample equipment 1: Electron Microscope
        eq1, created = Equipment.objects.get_or_create(
            infrastructure=infra,
            model_number='TEM-2100',
            defaults={
                'manufacturer': 'JEOL',
                'serial_number': 'SN12345678',
                'year_of_purchase': 2019,
                'status': 'operational',
                'is_available': True,
                'condition': 5,
                'requires_training': True
            }
        )
        if created:
            eq1.set_current_language('en')
            eq1.name = 'Transmission Electron Microscope'
            eq1.description = 'High-resolution TEM for nanoscale imaging'
            eq1.technical_details = 'Resolution: 0.19 nm, Acceleration voltage: 200 kV'
            eq1.sample_requirements = 'Samples must be <3mm diameter, ultrathin sections required'
            eq1.internal_notes = 'Requires booking at least 2 weeks in advance'
            eq1.set_current_language('pl')
            eq1.name = 'Transmisyjny Mikroskop Elektronowy'
            eq1.description = 'Wysokorozdzielczy TEM do obrazowania w nanoskali'
            eq1.technical_details = 'Rozdzielczość: 0.19 nm, Napięcie przyspieszające: 200 kV'
            eq1.sample_requirements = 'Próbki muszą być <3mm średnicy, wymagane ultracienkie sekcje'
            eq1.internal_notes = 'Wymaga rezerwacji co najmniej 2 tygodnie wcześniej'
            eq1.save()
            self.stdout.write(self.style.SUCCESS('Created TEM'))
        else:
            self.stdout.write('TEM already exists')

        # Create sample equipment 2: Spectrophotometer
        eq2, created = Equipment.objects.get_or_create(
            infrastructure=infra,
            model_number='UV-2600',
            defaults={
                'manufacturer': 'Shimadzu',
                'serial_number': 'SN87654321',
                'year_of_purchase': 2021,
                'status': 'operational',
                'is_available': True,
                'condition': 4,
                'requires_training': False
            }
        )
        if created:
            eq2.set_current_language('en')
            eq2.name = 'UV-Vis Spectrophotometer'
            eq2.description = 'Double-beam spectrophotometer for UV-Vis analysis'
            eq2.technical_details = 'Wavelength range: 185-900 nm, Bandwidth: 0.1, 0.5, 1.0, 2.0 nm'
            eq2.sample_requirements = 'Liquid or solid samples, standard cuvettes'
            eq2.internal_notes = 'Easy to use, good for routine measurements'
            eq2.set_current_language('pl')
            eq2.name = 'Spektrofotometr UV-Vis'
            eq2.description = 'Dwuwiązkowy spektrofotometr do analizy UV-Vis'
            eq2.technical_details = 'Zakres długości fal: 185-900 nm, Szerokość pasma: 0.1, 0.5, 1.0, 2.0 nm'
            eq2.sample_requirements = 'Próbki ciekłe lub stałe, standardowe kuwety'
            eq2.internal_notes = 'Łatwy w użyciu, dobry do rutynowych pomiarów'
            eq2.save()
            self.stdout.write(self.style.SUCCESS('Created Spectrophotometer'))
        else:
            self.stdout.write('Spectrophotometer already exists')

        # Create sample equipment 3: X-ray diffractometer (maintenance)
        if infrastructures.count() > 1:
            infra2 = infrastructures[1]
        else:
            infra2 = infra

        eq3, created = Equipment.objects.get_or_create(
            infrastructure=infra2,
            model_number='XRD-7000',
            defaults={
                'manufacturer': 'Shimadzu',
                'serial_number': 'SN11223344',
                'year_of_purchase': 2015,
                'status': 'maintenance',
                'is_available': False,
                'condition': 3,
                'requires_training': True
            }
        )
        if created:
            eq3.set_current_language('en')
            eq3.name = 'X-ray Diffractometer'
            eq3.description = 'XRD for crystallographic analysis'
            eq3.technical_details = 'Cu Kα radiation, 2θ range: 3-145°'
            eq3.sample_requirements = 'Powder or thin film samples'
            eq3.internal_notes = 'Currently under maintenance, expected back online next month'
            eq3.set_current_language('pl')
            eq3.name = 'Dyfraktometr Rentgenowski'
            eq3.description = 'XRD do analizy krystalograficznej'
            eq3.technical_details = 'Promieniowanie Cu Kα, zakres 2θ: 3-145°'
            eq3.sample_requirements = 'Próbki proszkowe lub cienkowarstwowe'
            eq3.internal_notes = 'Obecnie w konserwacji, oczekiwany powrót do użytku w przyszłym miesiącu'
            eq3.save()
            self.stdout.write(self.style.SUCCESS('Created XRD'))
        else:
            self.stdout.write('XRD already exists')

        self.stdout.write(self.style.SUCCESS('Sample equipment setup complete!'))