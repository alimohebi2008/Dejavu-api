from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Role, RoleType

User = get_user_model()


class AccountPermissionTests(APITestCase):
    def setUp(self):
        self.user_role, _ = Role.objects.get_or_create(name=RoleType.USER)
        self.admin_role, _ = Role.objects.get_or_create(name=RoleType.ADMIN)
        self.regular_user = User.objects.create_user(
            username="regular", password="test-password-123"
        )
        self.regular_user.role.add(self.user_role)
        # Deliberately not is_staff: access must be controlled by role.
        self.admin_user = User.objects.create_user(
            username="role-admin", password="test-password-123", is_staff=False
        )
        self.admin_user.role.add(self.admin_role)

    def test_anonymous_cannot_list_users(self):
        response = self.client.get("/api/accounts/users/")
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_user_role_cannot_list_users(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_role_can_list_users_without_staff_flag(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_flag_without_admin_role_does_not_grant_access(self):
        staff_only_user = User.objects.create_user(
            username="staff-only", password="test-password-123", is_staff=True
        )
        staff_only_user.role.add(self.user_role)
        self.client.force_authenticate(user=staff_only_user)
        response = self.client.get("/api/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_role_cannot_create_roles(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post("/api/accounts/roles/", {"name": "staff"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_requires_admin_role(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/accounts/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_detail_route_is_not_exposed(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/accounts/dashboard/1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
