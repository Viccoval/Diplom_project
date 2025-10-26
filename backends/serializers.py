from rest_framework import serializers
from .models import Product, Category, Store

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    store = StoreSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

