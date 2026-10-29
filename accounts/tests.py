from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from orders.models import Order

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

    def test_admin_can_create_user_with_hashed_password(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            "/api/accounts/users/",
            {
                "username": "new-account",
                "password": "A-secure-Passphrase-2026!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertNotIn("password", response.data)
        created_user = User.objects.get(username="new-account")
        self.assertTrue(created_user.check_password("A-secure-Passphrase-2026!"))
        self.assertNotEqual(created_user.password, "A-secure-Passphrase-2026!")

    def test_weak_password_is_rejected(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            "/api/accounts/users/",
            {"username": "weak-password-account", "password": "12345678"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(username="weak-password-account").exists())

    def test_admin_can_update_password_without_returning_it(self):
        self.client.force_authenticate(user=self.admin_user)
        new_password = "Another-secure-Passphrase-2026!"

        response = self.client.patch(
            f"/api/accounts/users/{self.regular_user.pk}/",
            {"password": new_password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertNotIn("password", response.data)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password(new_password))
        self.assertFalse(self.regular_user.check_password("test-password-123"))

    def test_updating_other_fields_preserves_existing_password(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.patch(
            f"/api/accounts/users/{self.regular_user.pk}/",
            {"first_name": "Updated"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password("test-password-123"))

    def test_created_user_without_password_gets_unusable_password(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            "/api/accounts/users/",
            {"username": "passwordless-account"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        created_user = User.objects.get(username="passwordless-account")
        self.assertFalse(created_user.has_usable_password())

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

    def test_cannot_delete_user_with_orders(self):
        order = Order.objects.create(user=self.regular_user, total_price="10.00")
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(f"/api/accounts/users/{self.regular_user.id}/")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(User.objects.filter(pk=self.regular_user.pk).exists())
        self.assertTrue(Order.objects.filter(pk=order.pk).exists())
