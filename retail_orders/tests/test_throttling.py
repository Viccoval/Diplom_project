from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from retail_orders.backends.models import Product, Store, OrderItem

class ThrottlingTestCase(APITestCase):
    def setUp(self):
        self.store = Store.objects.create(name='Test Store')
        self.add_to_cart_url = reverse('order-add-to-cart')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(name='Test Product', price=10.0, stock=1000, store=self.store)

    def test_anon_throttling_on_add_to_cart(self):
        """Тест: Анонимный пользователь превышает лимит (10/minute)."""
        data = {'product_id': self.product.id, 'quantity': 1}
        for _ in range(10):
            response = self.client.post(self.add_to_cart_url, data, format='json')
            self.assertIn(response.status_code,  [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
        response = self.client.post(self.add_to_cart_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_user_throttling_on_add_to_cart(self):
        """Тест: Аутентифицированный пользователь превышает лимит (100/minute)."""
        self.client.force_authenticate(user=self.user)
        data = {'product_id': self.product.id, 'quantity': 1}
        for _ in range(100):
            response = self.client.post(self.add_to_cart_url, data, format='json')
            self.assertIn(response.status_code, [200, 201, 400])
        response = self.client.post(self.add_to_cart_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

