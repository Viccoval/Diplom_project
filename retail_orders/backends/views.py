from rest_framework import status, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.utils import psa
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.shortcuts import render, redirect
from .forms import ProductForm
from .tasks import generate_thumbnails
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Order, OrderItem, Contact
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .serializers import ProductSerializer, OrderSerializer, ContactSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Класс для создания модели Product
    """
    queryset = Product.objects.select_related('store', 'category').all()
    serializer_class = ProductSerializer
    filterset_fields = ['store', 'price', 'category']
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        """
        Вызов генерации для создания продукта
        """
        product = serializer.save()
        if product.image:
            generate_thumbnails.delay(product.image.name, ['product_medium'])

    def perform_update(self, serializer):
        """
        Переопределяем после обновления продукта.
        """
        product = serializer.save()
        if product.image:
            generate_thumbnails.delay(product.image.name, ['product_medium'])

    def upload_product(request):
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save()
                if product.image:
                    generate_thumbnails.delay(product.image.name, ['product_medium'])
                return redirect('product_list')
        else:
            form = ProductForm()
        return render(request, 'upload_product.html', {'form': form})


class ContactViewSet(viewsets.ModelViewSet):
    """
    Класс для создания модели Contact
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    """
    Класс для создания заказов, модель Order
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'created_at']
    filter_backends = [DjangoFilterBackend]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Функция для сортировки заказов, возвращает только заказы текущего пользователя
        """
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'orderitem_set__product')

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        """
        Функция для добавления товара в корзину
        """
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Продукт не найден'}, status=status.HTTP_404_NOT_FOUND)

        if product.stock < quantity:
            return Response({'error': 'Недостаточно товара на складе'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({'message': 'Добавлено в корзину (аноним)'}, status=status.HTTP_201_CREATED)

        order, created = Order.objects.get_or_create(user=request.user, status='pending')

        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={'quantity': 0}
        )
        order_item.quantity += quantity
        order_item.save()

        return Response({'message': 'Добавлено в корзину'}, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['post'])
    def remove_from_cart(self, request, pk=None):
        order = self.get_object()
        item_id = request.data.get('item_id')

        try:
            item = OrderItem.objects.get(id=item_id, order=order)
            item.delete()
            order.save()
            return Response({'message': 'Удалено из корзины', 'total_price': order.total_price})
        except OrderItem.DoesNotExist:
            return Response({'error': 'Элемент не найден'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """
        Функция для обработки заказов
        """
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


class SocialAuthView(APIView):
    """
    Класс для обработки авторизации через Google
    """
    @psa('social:complete')
    def post(self, request, backend):
        """
        Обрабатывает POST-запрос с данными от Google
        """
        try:
            user = request.backend.do_auth(request.data.get('access_token'))
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                    }
                })
            else:
                return Response({'error': 'Попробуй еще раз'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
