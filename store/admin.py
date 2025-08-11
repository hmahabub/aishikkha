from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Product, Category, Order

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('title', 'author', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'product', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'product']
    search_fields = ['email', 'id', 'bkash_payment_id', 'trx_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False  # Prevent manual order creation