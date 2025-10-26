from django.contrib import admin
from .models import Store, Category, Product, Order, OrderItem, Contact

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'category', 'price', 'stock', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('store', 'category')
    list_editable = ('price', 'stock')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('total_price',)
    fields = ('user', 'status', 'created_at', 'updated_at', 'total_price')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    list_filter = ('product',)
    search_fields = ('product__name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    list_editable = ('phone',)
    ordering = ('-created_at',)

