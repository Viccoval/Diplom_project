from rest_framework import serializers
from .models import Product, Category, Store, Order, OrderItem, Contact

class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category
    """
    class Meta:
        model = Category
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Store
    """
    class Meta:
        model = Store
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Product
    """
    category = CategorySerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    stock = serializers.IntegerField(min_value=0)

    class Meta:
        model = Product
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для OrderItem
    """
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Order
    """
    orderitem_set = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'updated_at', 'orderitem_set', 'total_price']
        read_only_fields = ['user', 'created_at', 'updated_at']


class ContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Contact
    """
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['created_at']