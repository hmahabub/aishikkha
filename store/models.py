from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid

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