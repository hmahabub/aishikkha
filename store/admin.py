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
    list_display = ('reference_no', 'product', 'customer_name', 'email', 'is_paid', 'is_approved', 'created_at')
    list_filter = ('is_paid', 'is_approved')
    search_fields = ('reference_no', 'customer_name', 'email', 'phone')
    actions = ['approve_orders', 'mark_as_paid']

    def approve_orders(self, request, queryset):
        queryset.update(is_approved=True)
        # Send download links to customers
        for order in queryset:
            if order.is_paid and order.is_approved:
                send_mail(
                    _('আপনার বই ডাউনলোড করার লিঙ্ক'),
                    _('ধন্যবাদ! আপনার পেমেন্ট গ্রহণ করা হয়েছে। আপনি নিচের লিঙ্ক থেকে বইটি ডাউনলোড করতে পারেন:\n\n'
                      'ডাউনলোড লিঙ্ক: {}\n\n'
                      'রেফারেন্স নম্বর: {}').format(
                          order.product.pdf_file.url,
                          order.reference_no
                      ),
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=False,
                )
    approve_orders.short_description = _('নির্বাচিত অর্ডারসমূহ অনুমোদন করুন')

    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
    mark_as_paid.short_description = _('নির্বাচিত অর্ডারসমূহ পেমেন্ট সম্পন্ন হিসেবে চিহ্নিত করুন')