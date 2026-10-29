from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role, RoleType
from orders.models import Cart, CartItem, Order, Wishlist
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

    def test_cannot_add_inactive_product_to_wishlist(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/orders/wishlist/",
            {"product": self.inactive_product.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Wishlist.objects.filter(user=self.user, items__product=self.inactive_product).exists()
        )

    def test_cannot_change_cart_item_to_product_already_in_cart(self):
        active_product = Product.objects.create(
            category=self.category,
            title="Active product",
            slug="active-product",
            description="Available for sale",
            price="15.00",
            stock=5,
            is_active=True,
        )
        another_product = Product.objects.create(
            category=self.category,
            title="Another product",
            slug="another-product",
            description="Also available",
            price="20.00",
            stock=5,
            is_active=True,
        )
        cart = Cart.objects.create(user=self.user)
        first_item = CartItem.objects.create(
            cart=cart, product=active_product, quantity=1
        )
        second_item = CartItem.objects.create(
            cart=cart, product=another_product, quantity=1
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/orders/cart-items/{first_item.pk}/",
            {"product": another_product.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        first_item.refresh_from_db()
        self.assertEqual(first_item.product_id, active_product.pk)
        self.assertTrue(CartItem.objects.filter(pk=second_item.pk).exists())

    def test_detail_delete_does_not_delete_the_users_entire_wishlist(self):
        self.client.force_authenticate(user=self.user)
        self.client.get("/api/orders/wishlist/")

        response = self.client.delete("/api/orders/wishlist/999/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Wishlist.objects.filter(user=self.user).exists())
