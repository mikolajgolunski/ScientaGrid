from django.contrib.auth.models import AbstractUser
from django.db import models

class StaffRole(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('readonly', 'Read Only'),
    ]
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class UserProfile(AbstractUser):
    staff_role = models.ForeignKey(StaffRole, on_delete=models.PROTECT, related_name='users', null=True, blank=True)

    @property
    def is_readonly(self):
        return self.staff_role.name == 'readonly'

    @property
    def is_admin(self):
        return self.staff_role.name == 'admin'

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
