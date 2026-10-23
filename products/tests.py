from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role, RoleType
from .models import Category

User = get_user_model()


class ProductPermissionTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Test category", slug="test-category")
        self.user_role, _ = Role.objects.get_or_create(name=RoleType.USER)
        self.admin_role, _ = Role.objects.get_or_create(name=RoleType.ADMIN)
        self.regular_user = User.objects.create_user(username="shopper", password="test-password-123")
        self.regular_user.role.add(self.user_role)
        # Deliberately not is_staff: access must be controlled by role.
        self.admin_user = User.objects.create_user(username="shop-admin", password="test-password-123", is_staff=False)
        self.admin_user.role.add(self.admin_role)

    def test_anonymous_can_read_products(self):
        response = self.client.get("/api/products/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create_products(self):
        response = self.client.post("/api/products/products/", {})
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_user_role_cannot_create_products(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post("/api/products/products/", {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_role_can_create_categories_without_staff_flag(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post("/api/products/categories/", {
            "title": "New category", "slug": "new-category",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
