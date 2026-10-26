from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role, RoleType
from orders.models import Order, Wishlist
from products.models import Category, Product

User = get_user_model()


class OrderRelatedPermissionTests(APITestCase):
    def setUp(self):
        self.user_role, _ = Role.objects.get_or_create(name=RoleType.USER)
        self.user = User.objects.create_user(
            username="buyer", password="test-password-123"
        )
        self.user.role.add(self.user_role)
        self.roleless_user = User.objects.create_user(
            username="roleless", password="test-password-123"
        )
        self.category = Category.objects.create(
            title="Test category", slug="test-category"
        )
        self.inactive_product = Product.objects.create(
            category=self.category,
            title="Inactive product",
            slug="inactive-product",
            description="Not for sale",
            price="10.00",
            stock=5,
            is_active=False,
        )

    def test_user_role_can_access_own_cart(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/orders/cart/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_without_role_is_denied_cart_access(self):
        self.client.force_authenticate(user=self.roleless_user)
        response = self.client.get("/api/orders/cart/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_retrieve_another_users_order(self):
        other_user = User.objects.create_user(
            username="other-buyer", password="test-password-123"
        )
        other_user.role.add(self.user_role)
        other_order = Order.objects.create(user=other_user, total_price="10.00")

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/orders/orders/{other_order.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_add_inactive_product_to_cart(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/orders/cart-items/",
            {"product": self.inactive_product.id, "quantity": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detail_delete_does_not_delete_the_users_entire_wishlist(self):
        self.client.force_authenticate(user=self.user)
        self.client.get("/api/orders/wishlist/")

        response = self.client.delete("/api/orders/wishlist/999/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Wishlist.objects.filter(user=self.user).exists())
