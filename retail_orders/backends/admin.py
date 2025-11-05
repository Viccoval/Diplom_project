from django.contrib import admin
from .tasks import do_import
from django.urls import path
from django.contrib import messages
from .models import Store, Category, Product, Order, OrderItem, Contact
from django.http import HttpResponseRedirect
import json


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Store. Позволяет поиск по name, фильтрацию по created_at и сортировку по name.
    """
    list_display = ('name', 'address', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Админ класс для модели Category.
    """
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Админ класс для модели Product
    """
    change_list_template = 'admin/product_change_list.html'
    list_display = ('name', 'store', 'category', 'price', 'stock', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('store', 'category')
    list_editable = ('price', 'stock')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run-import/', self.run_import_view, name='run_import'),
        ]
        return custom_urls + urls

    def run_import_view(self, request):
        if request.method == 'POST':
            data_str = request.POST.get('data', '[]')
            try:
                data = json.loads(data_str)
                do_import.delay(data)
                messages.success(request, "Задача импорта запущена")
            except json.JSONDecodeError:
                messages.error(request, "Ошибка: Неверный формат JSON в данных.")
            return HttpResponseRedirect("../")
        else:
            return

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Админ класс для модели Order
    Позволяет фильтрацию по status и created_at, поиск по user__username, иерархическую навигацию по created_at.
    """
    list_display = ('id', 'user', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('total_price',)
    fields = ('user', 'status', 'created_at', 'updated_at', 'total_price')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Админ класс для модели OrderItem
    """
    list_display = ('order', 'product', 'quantity')
    list_filter = ('product',)
    search_fields = ('product__name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Админ класс для модели Contact
    """
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    list_editable = ('phone',)
    ordering = ('-created_at',)

