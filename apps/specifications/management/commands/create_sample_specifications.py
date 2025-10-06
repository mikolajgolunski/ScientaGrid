from django.core.management.base import BaseCommand
from apps.specifications.models import Specification, SpecificationValue
from apps.equipment.models import Equipment


class Command(BaseCommand):
    help = 'Creates sample specifications and links them to equipment'

    def handle(self, *args, **options):
        # Create Specifications

        # 1. Resolution (numeric)
        resolution, _ = Specification.objects.get_or_create(
            code='RESOLUTION',
            defaults={
                'data_type': 'numeric',
                'unit': 'nm',
                'category': 'performance',
                'display_order': 10,
                'is_filterable': True,
                'is_active': True
            }
        )
        resolution.set_current_language('en')
        resolution.name = 'Resolution'
        resolution.description = 'Maximum resolution achievable'
        resolution.unit_label = 'nanometers'
        resolution.set_current_language('pl')
        resolution.name = 'Rozdzielczość'
        resolution.description = 'Maksymalna osiągalna rozdzielczość'
        resolution.unit_label = 'nanometry'
        resolution.save()
        self.stdout.write(self.style.SUCCESS('Created Resolution specification'))

        # 2. Acceleration Voltage (range)
        voltage, _ = Specification.objects.get_or_create(
            code='ACC_VOLTAGE',
            defaults={
                'data_type': 'range',
                'unit': 'kV',
                'category': 'operational',
                'display_order': 20,
                'is_filterable': True,
                'is_active': True
            }
        )
        voltage.set_current_language('en')
        voltage.name = 'Acceleration Voltage'
        voltage.description = 'Operating voltage range'
        voltage.unit_label = 'kilovolts'
        voltage.set_current_language('pl')
        voltage.name = 'Napięcie Przyspieszające'
        voltage.description = 'Zakres napięcia roboczego'
        voltage.unit_label = 'kilowolty'
        voltage.save()
        self.stdout.write(self.style.SUCCESS('Created Voltage specification'))

        # 3. Wavelength Range (range)
        wavelength, _ = Specification.objects.get_or_create(
            code='WAVELENGTH',
            defaults={
                'data_type': 'range',
                'unit': 'nm',
                'category': 'performance',
                'display_order': 15,
                'is_filterable': True,
                'is_active': True
            }
        )
        wavelength.set_current_language('en')
        wavelength.name = 'Wavelength Range'
        wavelength.description = 'Spectral wavelength range'
        wavelength.unit_label = 'nanometers'
        wavelength.set_current_language('pl')
        wavelength.name = 'Zakres Długości Fal'
        wavelength.description = 'Spektralny zakres długości fal'
        wavelength.unit_label = 'nanometry'
        wavelength.save()
        self.stdout.write(self.style.SUCCESS('Created Wavelength specification'))

        # 4. Sample Size (range)
        sample_size, _ = Specification.objects.get_or_create(
            code='SAMPLE_SIZE',
            defaults={
                'data_type': 'range',
                'unit': 'mm',
                'category': 'sample',
                'display_order': 30,
                'is_filterable': True,
                'is_active': True
            }
        )
        sample_size.set_current_language('en')
        sample_size.name = 'Sample Size'
        sample_size.description = 'Acceptable sample size range'
        sample_size.unit_label = 'millimeters'
        sample_size.set_current_language('pl')
        sample_size.name = 'Rozmiar Próbki'
        sample_size.description = 'Akceptowalny zakres rozmiaru próbki'
        sample_size.unit_label = 'milimetry'
        sample_size.save()
        self.stdout.write(self.style.SUCCESS('Created Sample Size specification'))

        # 5. Automated Operation (boolean)
        automated, _ = Specification.objects.get_or_create(
            code='AUTOMATED',
            defaults={
                'data_type': 'boolean',
                'category': 'operational',
                'display_order': 40,
                'is_filterable': True,
                'is_active': True
            }
        )
        automated.set_current_language('en')
        automated.name = 'Automated Operation'
        automated.description = 'Can operate automatically without constant supervision'
        automated.set_current_language('pl')
        automated.name = 'Automatyczna Praca'
        automated.description = 'Może pracować automatycznie bez stałego nadzoru'
        automated.save()
        self.stdout.write(self.style.SUCCESS('Created Automated specification'))

        # 6. Sample Type (choice)
        sample_type, _ = Specification.objects.get_or_create(
            code='SAMPLE_TYPE',
            defaults={
                'data_type': 'choice',
                'choices': 'Solid, Liquid, Gas, Powder, Thin Film',
                'category': 'sample',
                'display_order': 25,
                'is_filterable': True,
                'is_active': True
            }
        )
        sample_type.set_current_language('en')
        sample_type.name = 'Sample Type'
        sample_type.description = 'Types of samples that can be analyzed'
        sample_type.set_current_language('pl')
        sample_type.name = 'Typ Próbki'
        sample_type.description = 'Typy próbek, które można analizować'
        sample_type.save()
        self.stdout.write(self.style.SUCCESS('Created Sample Type specification'))

        # 7. Temperature Range (range)
        temp_range, _ = Specification.objects.get_or_create(
            code='TEMP_RANGE',
            defaults={
                'data_type': 'range',
                'unit': '°C',
                'category': 'environmental',
                'display_order': 35,
                'is_filterable': True,
                'is_active': True
            }
        )
        temp_range.set_current_language('en')
        temp_range.name = 'Operating Temperature Range'
        temp_range.description = 'Temperature range for sample analysis'
        temp_range.unit_label = 'degrees Celsius'
        temp_range.set_current_language('pl')
        temp_range.name = 'Zakres Temperatur Pracy'
        temp_range.description = 'Zakres temperatur dla analizy próbek'
        temp_range.unit_label = 'stopnie Celsjusza'
        temp_range.save()
        self.stdout.write(self.style.SUCCESS('Created Temperature Range specification'))

        # Link specifications to equipment
        equipment = Equipment.objects.all()

        if equipment.exists():
            # Find TEM
            tem = equipment.filter(model_number='TEM-2100').first()
            if tem:
                SpecificationValue.objects.get_or_create(
                    equipment=tem,
                    specification=resolution,
                    defaults={
                        'numeric_value': 0.19,
                        'is_verified': True
                    }
                )
                SpecificationValue.objects.get_or_create(
                    equipment=tem,
                    specification=voltage,
                    defaults={
                        'range_min': 80,
                        'range_max': 200,
                        'is_verified': True
                    }
                )
                SpecificationValue.objects.get_or_create(
                    equipment=tem,
                    specification=sample_size,
                    defaults={
                        'range_max': 3,
                        'notes': 'Maximum diameter',
                        'is_verified': True
                    }
                )
                SpecificationValue.objects.get_or_create(
                    equipment=tem,
                    specification=automated,
                    defaults={
                        'boolean_value': False,
                        'is_verified': True
                    }
                )
                SpecificationValue.objects.get_or_create(
                    equipment=tem,
                    specification=sample_type,
                    defaults={
                        'choice_value': 'Solid, Thin Film',
                        'is_verified': True
                    }
                )
                self.stdout.write(self.style.SUCCESS('Linked specifications to TEM'))

            # Find Spectrophotometer
            spec = equipment.filter(model_number='UV-2600').first()
            if spec:
                SpecificationValue.objects.get_or_create(
                    equipment=spec,
                    specification=wavelength,
                    defaults={
                        'range_min': 185,
                        'range_max': 900,
                        'is_verified': True
                    }
                )
                SpecificationValue.objects.get_or_create(
                    equipment=spec,
                    specification=automated,
                    defaults={
                        'boolean_value': True,
                        'is_verified': True
                    }
                )
                SpecificationValue.objects.get_or_create(
                    equipment=spec,
                    specification=sample_type,
                    defaults={
                        'choice_value': 'Liquid, Solid',
                        'is_verified': True
                    }
                )
                SpecificationValue.objects.get_or_create(
                    equipment=spec,
                    specification=temp_range,
                    defaults={
                        'range_min': 15,
                        'range_max': 40,
                        'notes': 'Ambient temperature operation',
                        'is_verified': True
                    }
                )
                self.stdout.write(self.style.SUCCESS('Linked specifications to Spectrophotometer'))

        self.stdout.write(self.style.SUCCESS('Sample specifications setup complete!'))