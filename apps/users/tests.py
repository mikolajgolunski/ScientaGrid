from django.test import TestCase
from apps.users.models import UserProfile, StaffRole


class StaffRoleModelTest(TestCase):
    """Tests for StaffRole model."""

    def setUp(self):
        """Set up test data."""
        self.role = StaffRole.objects.create(
            name='admin'
        )

    def test_staff_role_creation(self):
        """Test staff role is created correctly."""
        self.assertEqual(self.role.name, 'admin')
        self.assertEqual(StaffRole.objects.count(), 1)

    def test_staff_role_str_representation(self):
        """Test staff role string representation."""
        self.assertEqual(str(self.role), 'Admin')


class UserProfileModelTest(TestCase):
    """Tests for UserProfile model."""

    def setUp(self):
        """Set up test data."""
        self.role = StaffRole.objects.create(name='admin')

        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            staff_role=self.role
        )

    def test_user_creation(self):
        """Test user is created correctly."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.staff_role, self.role)
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_user_str_representation(self):
        """Test user string representation."""
        self.assertIn('testuser', str(self.user))

    def test_user_password_is_hashed(self):
        """Test password is properly hashed."""
        self.assertNotEqual(self.user.password, 'testpass123')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_can_login(self):
        """Test user can authenticate."""
        from django.contrib.auth import authenticate
        user = authenticate(username='testuser', password='testpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_user_is_readonly_property(self):
        """Test is_readonly property."""
        readonly_role = StaffRole.objects.create(name='readonly')
        readonly_user = UserProfile.objects.create_user(
            username='readonly',
            password='pass',
            staff_role=readonly_role
        )

        self.assertTrue(readonly_user.is_readonly)
        self.assertFalse(self.user.is_readonly)

    def test_user_is_admin_property(self):
        """Test is_admin_role property."""
        self.assertTrue(self.user.is_admin)

    def test_superuser_creation(self):
        """Test superuser is created correctly."""
        superuser = UserProfile.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)