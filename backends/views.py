from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Order, OrderItem
from .serializers import ProductSerializer, OrderSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['store', 'price']

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        product_id = request.data['product_id']
        quantity = request.data.get('quantity', 1)
        order, created = Order.objects.get_or_create(user=request.user, status='pending')
        OrderItem.objects.create(order=order, product_id=product_id, quantity=quantity)
        return Response({'message': 'Добавлено в корзину'}, status=status.HTTP_201_CREATED)
