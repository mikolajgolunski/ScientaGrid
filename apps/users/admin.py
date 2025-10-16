from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.db import models

from .models import StaffRole, UserProfile

from ScientaGrid.admin import admin_site


@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(UserAdmin):
    """Custom admin for UserProfile with StaffRole and Group management."""
    
    fieldsets = UserAdmin.fieldsets + (
        ('Staff Info', {'fields': ('staff_role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Staff Info', {'fields': ('staff_role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'staff_role', 'get_groups', 'is_active', 'is_staff')
    list_filter = ('staff_role', 'groups', 'is_active', 'is_staff')
    filter_horizontal = ('groups', 'user_permissions')
    
    def get_groups(self, obj):
        """Display user's groups in the list view."""
        return ", ".join([group.name for group in obj.groups.all()]) or "No groups"
    get_groups.short_description = "Groups"
    
    def save_model(self, request, obj, form, change):
        """Automatically assign groups based on staff role."""
        super().save_model(request, obj, form, change)
        
        if obj.staff_role:
            # Clear existing groups first
            obj.groups.clear()
            
            # Assign groups based on staff role
            if obj.staff_role.name == 'admin':
                try:
                    admin_group = Group.objects.get(name='ScientaGrid Admin')
                    obj.groups.add(admin_group)
                except Group.DoesNotExist:
                    pass
            elif obj.staff_role.name == 'readonly':
                try:
                    viewer_group = Group.objects.get(name='Data Viewer')
                    obj.groups.add(viewer_group)
                except Group.DoesNotExist:
                    pass


@admin.register(StaffRole, site=admin_site)
class StaffRoleAdmin(admin.ModelAdmin):
    """Admin for StaffRole model."""
    list_display = ('name', 'get_display_name', 'user_count')
    search_fields = ('name',)
    readonly_fields = ('user_count',)
    
    def get_display_name(self, obj):
        """Show the human-readable name."""
        return obj.get_name_display()
    get_display_name.short_description = "Display Name"
    
    def user_count(self, obj):
        """Show how many users have this role."""
        return obj.users.count()
    user_count.short_description = "Users with this role"


@admin.register(Group, site=admin_site)
class CustomGroupAdmin(GroupAdmin):
    """Enhanced Group admin with permission details."""
    list_display = ('name', 'permission_count')
    
    def permission_count(self, obj):
        """Show number of permissions assigned to the group."""
        return obj.permissions.count()
    permission_count.short_description = "Permissions"
