from django.core.management.base import BaseCommand
from apps.search.services import SearchService


class Command(BaseCommand):
    help = 'Test search functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            'query',
            type=str,
            help='Search query text',
        )
        parser.add_argument(
            '--type',
            type=str,
            default='infrastructure',
            help='Search type (infrastructure, equipment, service, research_problem, unified)',
        )

    def handle(self, *args, **options):
        query = options['query']
        search_type = options['type']

        self.stdout.write(f'\nSearching for: "{query}"')
        self.stdout.write(f'Search type: {search_type}\n')

        if search_type == 'unified':
            results = SearchService.unified_search(query)

            for result_type, data in results.items():
                self.stdout.write(self.style.SUCCESS(f'\n{result_type.upper()}:'))
                self.stdout.write(f'Found {data["count"]} results in {data["time_ms"]}ms')

                for obj in data['results']:
                    self.stdout.write(f'  - {obj}')

        elif search_type == 'infrastructure':
            results, exec_time, count = SearchService.search_infrastructures(query)
            self.stdout.write(self.style.SUCCESS(f'Found {count} infrastructures in {exec_time}ms'))
            for infra in results[:10]:
                self.stdout.write(f'  - {infra.name} ({infra.city.name})')

        elif search_type == 'equipment':
            results, exec_time, count = SearchService.search_equipment(query)
            self.stdout.write(self.style.SUCCESS(f'Found {count} equipment in {exec_time}ms'))
            for eq in results[:10]:
                self.stdout.write(f'  - {eq.name} at {eq.infrastructure.name}')

        elif search_type == 'service':
            results, exec_time, count = SearchService.search_services(query)
            self.stdout.write(self.style.SUCCESS(f'Found {count} services in {exec_time}ms'))
            for svc in results[:10]:
                self.stdout.write(f'  - {svc.name}')

        elif search_type == 'research_problem':
            results, exec_time, count = SearchService.search_research_problems(query)
            self.stdout.write(self.style.SUCCESS(f'Found {count} research problems in {exec_time}ms'))
            for prob in results[:10]:
                self.stdout.write(f'  - {prob.title}')

        else:
            self.stdout.write(self.style.ERROR(f'Unknown search type: {search_type}'))