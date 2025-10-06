from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps


class Command(BaseCommand):
    help = "Setup permissions and groups for ScientaGrid users"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Setting up permissions and groups..."))
        
        # Create basic groups
        admin_group, created = Group.objects.get_or_create(name="ScientaGrid Admin")
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created group: {admin_group.name}"))
        else:
            self.stdout.write(f"Group already exists: {admin_group.name}")
            
        viewer_group, created = Group.objects.get_or_create(name="Data Viewer")
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created group: {viewer_group.name}"))
        else:
            self.stdout.write(f"Group already exists: {viewer_group.name}")

        # Clear existing permissions for clean setup
        admin_group.permissions.clear()
        viewer_group.permissions.clear()
        
        # Get all apps in the ScientaGrid project
        scientagrid_apps = [
            "users", "institutions", "locations", "infrastructures", "equipment", 
            "services", "access", "research_problems", "taxonomy", "specifications", 
            "search", "matching", "documents", "scheduling", "audit", "api"
        ]
        
        # Admin group gets all permissions
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)
        self.stdout.write(self.style.SUCCESS(f"Assigned {all_permissions.count()} permissions to {admin_group.name}"))
        
        # Viewer group gets only view permissions
        view_permissions = Permission.objects.filter(codename__startswith="view_")
        viewer_group.permissions.set(view_permissions)
        self.stdout.write(self.style.SUCCESS(f"Assigned {view_permissions.count()} view permissions to {viewer_group.name}"))
        
        # Also add some basic Django permissions for viewer group
        basic_permissions = Permission.objects.filter(
            codename__in=["view_group", "view_permission", "view_contenttype", "view_session"]
        )
        viewer_group.permissions.add(*basic_permissions)
        
        self.stdout.write(self.style.SUCCESS("Permission setup completed successfully!"))