from django.core.management.base import BaseCommand

from apps.locations.models import City, Country, Region


class Command(BaseCommand):
    help = "Creates Poland with Kraków location data"

    def handle(self, *args, **options):
        # Create Poland
        poland, created = Country.objects.get_or_create(code="PL")
        poland.set_current_language("en")
        poland.name = "Poland"
        poland.set_current_language("pl")
        poland.name = "Polska"
        poland.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Poland created successfully"))

        # Create Małopolska voivodeship
        malopolska, created = Region.objects.get_or_create(
            country=poland,
            code="MA"
        )
        malopolska.set_current_language("en")
        malopolska.name = "Malopolska"
        malopolska.set_current_language("pl")
        malopolska.name = "Małopolska"
        malopolska.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Małopolska created successfully"))

        # Create Kraków
        krakow, created = City.objects.get_or_create(
            region=malopolska,
            defaults={"postal_code": "30-000"}
        )
        krakow.set_current_language("en")
        krakow.name = "Krakow"
        krakow.set_current_language("pl")
        krakow.name = "Kraków"
        krakow.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Kraków created successfully"))

        self.stdout.write(self.style.SUCCESS("All locations created successfully"))