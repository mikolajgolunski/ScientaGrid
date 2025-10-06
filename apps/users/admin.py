from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, StaffRole

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    # You can customize which fields appear in list/detail view
    fieldsets = UserAdmin.fieldsets + (
        ('Staff Info', {'fields': ('staff_role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Staff Info', {'fields': ('staff_role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'staff_role', 'is_active', 'is_staff')
    list_filter = ('staff_role', 'is_active', 'is_staff')

@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name',)
