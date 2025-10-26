
from django.urls import path
from .views import ProductViewSet, OrderViewSet, ContactViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'contacts', ContactViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = router.urls