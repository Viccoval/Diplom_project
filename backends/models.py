from django.db import models
from django.contrib.auth.models import User

class Store(models.Model):  # Розничная сеть
    name = models.CharField(max_length=100)
    address = models.TextField()

class Product(models.Model):  # Товар
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()

class Order(models.Model):  # Заказ
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[('pending', 'Ожидает'), ('completed', 'Завершен')])
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):  # Элемент заказа (корзина)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


