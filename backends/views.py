from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Order, OrderItem  # <-- Все модели из backends
from .serializers import ProductSerializer, OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('store', 'category').all()
    serializer_class = ProductSerializer
    filterset_fields = ['store', 'price', 'category']
    filter_backends = [DjangoFilterBackend]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'created_at']
    filter_backends = [DjangoFilterBackend]  # <-- Добавил для консистентности

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'orderitem_set__product')

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)

        if product.stock < quantity:
            return Response({'error': 'Недостаточно товара на складе'}, status=status.HTTP_400_BAD_REQUEST)

        order, created = Order.objects.get_or_create(user=request.user, status='pending')
        OrderItem.objects.create(order=order, product=product, quantity=quantity)

        order.total_price += product.price * quantity
        order.save()

        return Response({'message': 'Добавлено в корзину', 'total_price': order.total_price},
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_from_cart(self, request, pk=None):
        order = self.get_object()
        item_id = request.data.get('item_id')

        try:
            item = OrderItem.objects.get(id=item_id, order=order)
            order.total_price -= item.product.price * item.quantity
            item.delete()
            order.save()
            return Response({'message': 'Удалено из корзины', 'total_price': order.total_price})
        except OrderItem.DoesNotExist:
            return Response({'error': 'Элемент не найден'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': 'Заказ уже обработан'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for item in order.orderitem_set.all():
                if item.product.stock < item.quantity:
                    return Response({'error': f'Недостаточно {item.product.name}'}, status=status.HTTP_400_BAD_REQUEST)
                item.product.stock -= item.quantity
                item.product.save()

            order.status = 'completed'
            order.save()

        return Response({'message': 'Заказ оформлен', 'total_price': order.total_price})

