from django.core.management.base import BaseCommand
from apps.institutions.models import Institution
from apps.locations.models import City


class Command(BaseCommand):
    help = 'Creates sample institutions in Kraków'

    def handle(self, *args, **options):
        try:
            # Better query - filter first, then get the actual object
            cities = City.objects.filter(translations__name='Kraków')
            if cities.count() == 0:
                self.stdout.write(self.style.ERROR(
                    'Kraków not found. Run create_poland_locations first.'
                ))
                return
            krakow = cities.first()  # Get the first (and should be only) City object

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error finding Kraków: {e}'))
            return

        # Jagiellonian University
        uj, created = Institution.objects.get_or_create(
            website='https://www.uj.edu.pl',
            defaults={
                'city': krakow,
                'institution_type': 'university',
                'email': 'info@uj.edu.pl',
                'phone': '+48 12 663 10 00'
            }
        )
        if created:
            uj.set_current_language('en')
            uj.name = 'Jagiellonian University'
            uj.description = 'The oldest university in Poland, founded in 1364'
            uj.address = 'Gołębia 24'
            uj.set_current_language('pl')
            uj.name = 'Uniwersytet Jagielloński'
            uj.description = 'Najstarsza uczelnia w Polsce, założona w 1364 roku'
            uj.address = 'Gołębia 24'
            uj.save()
            self.stdout.write(self.style.SUCCESS('Created Jagiellonian University'))
        else:
            self.stdout.write('Jagiellonian University already exists')

        # AGH University
        agh, created = Institution.objects.get_or_create(
            website='https://www.agh.edu.pl',
            defaults={
                'city': krakow,
                'institution_type': 'university',
                'email': 'info@agh.edu.pl',
                'phone': '+48 12 617 30 00'
            }
        )
        if created:
            agh.set_current_language('en')
            agh.name = 'AGH University of Science and Technology'
            agh.description = 'Technical university specializing in engineering and technology'
            agh.address = 'al. Mickiewicza 30'
            agh.set_current_language('pl')
            agh.name = 'Akademia Górniczo-Hutnicza'
            agh.description = 'Uczelnia techniczna specjalizująca się w inżynierii i technologii'
            agh.address = 'al. Mickiewicza 30'
            agh.save()
            self.stdout.write(self.style.SUCCESS('Created AGH University'))
        else:
            self.stdout.write('AGH University already exists')

        self.stdout.write(self.style.SUCCESS('Sample institutions setup complete!'))