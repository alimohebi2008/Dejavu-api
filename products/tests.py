from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role, RoleType
from products.models import Category, Product, ProductColor, ProductDiscount, ProductSize

User = get_user_model()


class ProductPermissionTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            title="Test category", slug="test-category"
        )
        self.size = ProductSize.objects.create(
            title="Medium", width="10.00", length="20.00"
        )
        self.color = ProductColor.objects.create(title="Red", hex_code="#FF0000")
        self.product = Product.objects.create(
            category=self.category,
            title="Existing product",
            slug="existing-product",
            description="For tests",
            price="25.00",
            stock=5,
        )
        self.user_role, _ = Role.objects.get_or_create(name=RoleType.USER)
        self.admin_role, _ = Role.objects.get_or_create(name=RoleType.ADMIN)
        self.regular_user = User.objects.create_user(
            username="shopper", password="test-password-123"
        )
        self.regular_user.role.add(self.user_role)
        # Deliberately not is_staff: access must be controlled by role.
        self.admin_user = User.objects.create_user(
            username="shop-admin", password="test-password-123", is_staff=False
        )
        self.admin_user.role.add(self.admin_role)

    def test_anonymous_can_read_products(self):
        response = self.client.get("/api/products/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create_products(self):
        response = self.client.post("/api/products/products/", {})
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_user_role_cannot_create_products(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post("/api/products/products/", {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_role_can_create_categories_without_staff_flag(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/api/products/categories/",
            {"title": "New category", "slug": "new-category"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_admin_can_create_product_with_category_sizes_and_colors(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            "/api/products/products/",
            {
                "category": self.category.id,
                "title": "API-created product",
                "slug": "api-created-product",
                "description": "Created through the API",
                "price": "25.00",
                "stock": 4,
                "is_active": True,
                "sizes": [self.size.id],
                "colors": [self.color.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["category"]["id"], self.category.id)
        self.assertEqual(response.data["sizes"][0]["id"], self.size.id)
        self.assertEqual(response.data["colors"][0]["id"], self.color.id)

    def test_fixed_discount_cannot_exceed_product_price(self):
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        response = self.client.post(
            "/api/products/product_discounts/",
            {
                "product": self.product.id,
                "discount_type": "fixed",
                "value": "30.00",
                "start_at": now.isoformat(),
                "end_at": (now + timedelta(days=1)).isoformat(),
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_public_product_list_hides_inactive_products(self):
        inactive_product = Product.objects.create(
            category=self.category,
            title="Hidden product",
            slug="hidden-product",
            description="Should not be public",
            price="10.00",
            stock=1,
            is_active=False,
        )
        response = self.client.get("/api/products/products/")
        self.assertNotIn(inactive_product.id, [item["id"] for item in response.data])

    def test_public_category_list_hides_inactive_categories(self):
        inactive_category = Category.objects.create(
            title="Hidden category", slug="hidden-category", is_active=False
        )
        response = self.client.get("/api/products/categories/")
        self.assertNotIn(inactive_category.id, [item["id"] for item in response.data])

    def test_public_size_list_hides_inactive_sizes(self):
        inactive_size = ProductSize.objects.create(
            title="Inactive size", width="12.00", length="24.00", is_active=False
        )
        response = self.client.get("/api/products/sizes/")
        self.assertNotIn(inactive_size.id, [item["id"] for item in response.data])

    def test_public_color_list_hides_inactive_colors(self):
        inactive_color = ProductColor.objects.create(
            title="Inactive color", hex_code="#00FF00", is_active=False
        )
        response = self.client.get("/api/products/product_colors/")
        self.assertNotIn(inactive_color.id, [item["id"] for item in response.data])

    def test_public_discount_list_hides_future_discounts(self):
        now = timezone.now()
        discount = ProductDiscount.objects.create(
            product=self.product,
            discount_type="percentage",
            value="10.00",
            start_at=now + timedelta(days=1),
            end_at=now + timedelta(days=2),
            is_active=True,
        )
        response = self.client.get("/api/products/product_discounts/")
        self.assertNotIn(discount.id, [item["id"] for item in response.data])
