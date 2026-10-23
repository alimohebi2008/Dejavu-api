from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role, RoleType

User = get_user_model()


class OrderRelatedPermissionTests(APITestCase):
    def setUp(self):
        self.user_role, _ = Role.objects.get_or_create(name=RoleType.USER)
        self.user = User.objects.create_user(username="buyer", password="test-password-123")
        self.user.role.add(self.user_role)
        self.roleless_user = User.objects.create_user(username="roleless", password="test-password-123")

    def test_user_role_can_access_own_cart(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/orders/cart/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_without_role_is_denied_cart_access(self):
        self.client.force_authenticate(user=self.roleless_user)
        response = self.client.get("/api/orders/cart/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
