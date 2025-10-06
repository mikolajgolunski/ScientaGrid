from django.core.management.base import BaseCommand

from apps.users.models import StaffRole


class Command(BaseCommand):
    help = 'Create initial staff roles'

    def handle(self, *args, **options):
        admin_role, created = StaffRole.objects.get_or_create(
            name='admin',
            # defaults={'description': 'Full access to all features'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Admin role created successfully'))
        else:
            self.stdout.write('Admin role already exists')

        readonly_role, created = StaffRole.objects.get_or_create(
            name='readonly',
            # defaults={'description': 'Read-only access'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Read-only role created successfully'))
        else:
            self.stdout.write('Read-only role already exists')