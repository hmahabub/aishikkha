from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Product, Category, Order, Review
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'product_name', 'rating_display', 
        'status_display', 'created_at', 'action_buttons'
    ]
    list_filter = ['status', 'rating', 'created_at', 'product']
    search_fields = ['product__name', 'name', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'approved_at', 'approved_by']
    list_per_page = 25
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'name', 'email')
        }),
        ('Review Content', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'approved_at', 'approved_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'reject_reviews', 'mark_as_pending']
    
    def product_name(self, obj):
        """Display product name with link"""
        url = reverse('admin:store_review_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.title)
    product_name.short_description = 'Product'
    
    
    def rating_display(self, obj):
        """Display rating with stars"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107;">{}</span> ({})', stars, obj.rating)
    rating_display.short_description = 'Rating'
    
    def status_display(self, obj):
        """Display status with colors"""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>', 
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def action_buttons(self, obj):
        """Display action buttons"""
        buttons = []
        if obj.status == 'pending':
            approve_url = f'/admin/store/review/{obj.id}/approve/'
            reject_url = f'/admin/store/review/{obj.id}/reject/'
            buttons.append(f'<a class="btn btn-success btn-sm" href="#" onclick="approveReview({obj.id})">Approve</a>')
            buttons.append(f'<a class="btn btn-danger btn-sm" href="#" onclick="rejectReview({obj.id})">Reject</a>')
        elif obj.status == 'approved':
            buttons.append('<span class="text-success">✓ Approved</span>')
        elif obj.status == 'rejected':
            buttons.append('<span class="text-danger">✗ Rejected</span>')
        
        return format_html(' '.join(buttons))
    action_buttons.short_description = 'Actions'
    
    def approve_reviews(self, request, queryset):
        """Bulk approve reviews"""
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_at=timezone.now(),
            approved_by=request.user
        )
        self.message_user(request, f'{updated} reviews approved successfully.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def reject_reviews(self, request, queryset):
        """Bulk reject reviews"""
        updated = queryset.filter(status__in=['pending', 'approved']).update(
            status='rejected',
            approved_at=None,
            approved_by=None
        )
        self.message_user(request, f'{updated} reviews rejected.')
    reject_reviews.short_description = 'Reject selected reviews'
    
    def mark_as_pending(self, request, queryset):
        """Mark reviews as pending"""
        updated = queryset.exclude(status='pending').update(
            status='pending',
            approved_at=None,
            approved_by=None
        )
        self.message_user(request, f'{updated} reviews marked as pending.')
    mark_as_pending.short_description = 'Mark as pending'
    
    def save_model(self, request, obj, form, change):
        """Auto-set approval info when status is changed to approved"""
        if change and 'status' in form.changed_data:
            if obj.status == 'approved':
                obj.approved_at = timezone.now()
                obj.approved_by = request.user
            elif obj.status in ['pending', 'rejected']:
                obj.approved_at = None
                obj.approved_by = None
        
        super().save_model(request, obj, form, change)

    class Media:
        js = ('admin/js/review_admin.js',)  # Custom JS for AJAX actions