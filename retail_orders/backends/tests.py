from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from retail_orders.backends.models import Product, Order, OrderItem, Contact, Store, Category

class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category')
        self.client.force_authenticate(user=self.user)
        self.store = Store.objects.create(name='Test Store')
        self.product = Product.objects.create(store=self.store, name='Test Product', price=10.00, stock=100)

    def test_list_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_retrieve_product(self):
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_create_product(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'New Product', 'price': 20.0, 'stock': 10, 'store': self.store.id, 'category': self.category.id}
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_product(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Updated Product'}
        response = self.client.patch(f'/api/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_product(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class ContactViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.contact = Contact.objects.create(user=self.user, phone='123456789', address='Test Address')

    def test_list_contacts(self):
        response = self.client.get('/api/contacts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_contact_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {'phone': '987654321', 'address': 'New Address'}
        response = self.client.post('/api/contacts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_contact_unauthenticated(self):
        data = {'phone': '987654321', 'address': 'New Address'}
        response = self.client.post('/api/contacts/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class OrderViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.store = Store.objects.create(name='Test Store')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', price=10.0, stock=5, store=self.store, category=self.category)
        self.order = Order.objects.create(user=self.user, status='pending')

    def test_list_orders_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_to_cart_success(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post('/api/orders/add_to_cart/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_price'], 20.0)

    def test_add_to_cart_insufficient_stock(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': self.product.id, 'quantity': 10}
        response = self.client.post('/api/orders/add_to_cart/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_to_cart_product_not_found(self):
        self.client.force_authenticate(user=self.user)
        data = {'product_id': 999, 'quantity': 1}
        response = self.client.post('/api/orders/add_to_cart/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_from_cart_success(self):
        self.client.force_authenticate(user=self.user)
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2)
        self.order.save()
        data = {'item_id': item.id}
        response = self.client.post(f'/api/orders/{self.order.id}/remove_from_cart/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_price'], 0)

    def test_remove_from_cart_item_not_found(self):
        self.client.force_authenticate(user=self.user)
        data = {'item_id': 999}
        response = self.client.post(f'/api/orders/{self.order.id}/remove_from_cart/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkout_success(self):
        self.client.force_authenticate(user=self.user)
        OrderItem.objects.create(order=self.order, product=self.product, quantity=2)
        response = self.client.post(f'/api/orders/{self.order.id}/checkout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_checkout_insufficient_stock(self):
        self.client.force_authenticate(user=self.user)
        OrderItem.objects.create(order=self.order, product=self.product, quantity=10)
        response = self.client.post(f'/api/orders/{self.order.id}/checkout/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_already_completed(self):
        self.client.force_authenticate(user=self.user)
        self.order.status = 'completed'
        self.order.save()
        response = self.client.post(f'/api/orders/{self.order.id}/checkout/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

