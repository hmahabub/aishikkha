from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(_("Category Name"), max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
    
    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(_("Title"), max_length=200)
    author = models.CharField(_("Writer"), max_length=100)
    description = models.TextField(_("Description"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("Category"))
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    pdf_file = models.FileField(_("PDF File"), upload_to='pdfs/')
    sample_pdf_file = models.FileField(_(" Sample PDF File"), upload_to='sample_pdfs/')
    thumbnail = models.ImageField(_("Thumbnail(200pxX200px)"), upload_to='thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Ebook")
        verbose_name_plural = _("Ebooks")
    
    def __str__(self):
        return self.title

    def get_average_rating(self):
        """Calculate average rating from approved reviews"""
        approved_reviews = self.reviews.filter(status='approved')
        if approved_reviews.exists():
            return round(approved_reviews.aggregate(
                models.Avg('rating')
            )['rating__avg'], 1)
        return 0
    
    def get_rating_count(self):
        """Get count of approved reviews"""
        return self.reviews.filter(status='approved').count()
    
    def get_rating_distribution(self):
        """Get distribution of ratings"""
        approved_reviews = self.reviews.filter(status='approved')
        distribution = {}
        for i in range(1, 6):
            distribution[i] = approved_reviews.filter(rating=i).count()
        return distribution

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100, help_text="Your display name")
    email = models.EmailField()
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, help_text="Review title")
    comment = models.TextField(help_text="Your detailed review")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_reviews'
    )
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'email']  # One review per user per product
        
    def __str__(self):
        return f'{self.name} - {self.product.title} ({self.rating}/5)'
    
    def get_star_display(self):
        """Return stars for template display"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    def save(self, *args, **kwargs):
        if self.status == 'approved' and not self.approved_at:
            from django.utils import timezone
            self.approved_at = timezone.now()
        super().save(*args, **kwargs)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(_("Customer Name"), max_length=100)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone No."), max_length=15)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bkash_payment_id = models.CharField(max_length=100, blank=True, null=True)
    trx_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.email}"