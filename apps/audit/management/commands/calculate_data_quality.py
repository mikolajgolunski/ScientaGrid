from django.core.management.base import BaseCommand
from apps.audit.models import DataQualityMetric
from apps.infrastructures.models import Infrastructure
from apps.equipment.models import Equipment
from apps.services.models import Service


class Command(BaseCommand):
    help = 'Calculate data quality metrics for all objects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Calculate only for specific model (infrastructure, equipment, service)',
        )

    def handle(self, *args, **options):
        models_to_process = []

        if options['model']:
            model_map = {
                'infrastructure': Infrastructure,
                'equipment': Equipment,
                'service': Service,
            }
            model = model_map.get(options['model'].lower())
            if model:
                models_to_process = [model]
            else:
                self.stdout.write(self.style.ERROR(f'Unknown model: {options["model"]}'))
                return
        else:
            models_to_process = [Infrastructure, Equipment, Service]

        total_calculated = 0

        for model in models_to_process:
            self.stdout.write(f'\nProcessing {model.__name__}...')
            objects = model.objects.all()

            for obj in objects:
                try:
                    metric = DataQualityMetric.calculate_for_object(obj)
                    total_calculated += 1
                    self.stdout.write(
                        f'  {obj}: Quality={metric.quality_score}%, Completeness={metric.completeness_score}%'
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error processing {obj}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\nCalculated metrics for {total_calculated} objects'))