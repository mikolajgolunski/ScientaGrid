from django.core.management.base import BaseCommand
from apps.infrastructures.models import Infrastructure, ContactPerson
from apps.institutions.models import Institution
from apps.locations.models import City
from apps.users.models import UserProfile


class Command(BaseCommand):
    help = 'Creates sample research infrastructures in Kraków'

    def handle(self, *args, **options):
        # Get Kraków
        try:
            krakow = City.objects.filter(translations__name='Kraków').first()
            if not krakow:
                self.stdout.write(self.style.ERROR('Kraków not found'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error finding Kraków: {e}'))
            return

        # Get institutions
        try:
            uj = Institution.objects.filter(website='https://www.uj.edu.pl').first()
            agh = Institution.objects.filter(website='https://www.agh.edu.pl').first()

            if not uj or not agh:
                self.stdout.write(self.style.ERROR(
                    'Institutions not found. Run create_sample_institutions first.'
                ))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error finding institutions: {e}'))
            return

        # Get first superuser for created_by (if exists)
        created_by = UserProfile.objects.filter(is_superuser=True).first()

        # Create sample infrastructure at UJ
        infra1, created = Infrastructure.objects.get_or_create(
            website='https://www.if.uj.edu.pl',
            defaults={
                'institution': uj,
                'city': krakow,
                'email': 'contact@if.uj.edu.pl',
                'phone': '+48 12 664 46 00',
                'reliability': 5,
                'is_active': True,
                'is_verified': True,
                'created_by': created_by
            }
        )
        if created:
            infra1.set_current_language('en')
            infra1.name = 'Faculty of Physics, Astronomy and Applied Computer Science'
            infra1.description = 'Advanced research facilities for physics and astronomy research'
            infra1.internal_comments = 'Excellent collaboration history'
            infra1.set_current_language('pl')
            infra1.name = 'Wydział Fizyki, Astronomii i Informatyki Stosowanej'
            infra1.description = 'Zaawansowane laboratoria do badań z zakresu fizyki i astronomii'
            infra1.internal_comments = 'Doskonała historia współpracy'
            infra1.save()

            # Add contact person
            ContactPerson.objects.create(
                infrastructure=infra1,
                first_name='Jan',
                last_name='Kowalski',
                position='Laboratory Manager',
                email='jan.kowalski@uj.edu.pl',
                phone='+48 12 664 46 10',
                is_primary=True
            )

            self.stdout.write(self.style.SUCCESS('Created UJ infrastructure'))
        else:
            self.stdout.write('UJ infrastructure already exists')

        # Create sample infrastructure at AGH
        infra2, created = Infrastructure.objects.get_or_create(
            website='https://www.agh.edu.pl/en/science',
            defaults={
                'institution': agh,
                'city': krakow,
                'email': 'science@agh.edu.pl',
                'phone': '+48 12 617 30 00',
                'reliability': 4,
                'is_active': True,
                'is_verified': True,
                'created_by': created_by
            }
        )
        if created:
            infra2.set_current_language('en')
            infra2.name = 'AGH Centre of Energy'
            infra2.description = 'Research infrastructure for energy and environmental studies'
            infra2.internal_comments = 'New facility, still building reputation'
            infra2.set_current_language('pl')
            infra2.name = 'Centrum Energetyki AGH'
            infra2.description = 'Infrastruktura badawcza dla badań energetycznych i środowiskowych'
            infra2.internal_comments = 'Nowy obiekt, buduje jeszcze reputację'
            infra2.save()

            # Add contact person
            ContactPerson.objects.create(
                infrastructure=infra2,
                first_name='Anna',
                last_name='Nowak',
                position='Research Coordinator',
                email='anna.nowak@agh.edu.pl',
                phone='+48 12 617 30 50',
                is_primary=True
            )

            self.stdout.write(self.style.SUCCESS('Created AGH infrastructure'))
        else:
            self.stdout.write('AGH infrastructure already exists')

        self.stdout.write(self.style.SUCCESS('Sample infrastructures setup complete!'))