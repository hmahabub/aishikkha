from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(_("বিভাগের নাম"), max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = _("বিভাগ")
        verbose_name_plural = _("বিভাগসমূহ")
    
    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(_("শিরোনাম"), max_length=200)
    author = models.CharField(_("লেখক"), max_length=100)
    description = models.TextField(_("বিবরণ"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("বিভাগ"))
    price = models.DecimalField(_("মূল্য"), max_digits=10, decimal_places=2)
    pdf_file = models.FileField(_("PDF ফাইল"), upload_to='pdfs/')
    thumbnail = models.ImageField(_("থাম্বনেইল"), upload_to='thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("পণ্য")
        verbose_name_plural = _("পণ্যসমূহ")
    
    def __str__(self):
        return self.title

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("পণ্য"))
    customer_name = models.CharField(_("ক্রেতার নাম"), max_length=100)
    email = models.EmailField(_("ইমেইল"))
    phone = models.CharField(_("ফোন নম্বর"), max_length=15)
    reference_no = models.CharField(_("রেফারেন্স নম্বর"), max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(_("পেমেন্ট সম্পন্ন"), default=False)
    is_approved = models.BooleanField(_("অনুমোদিত"), default=False)
    
    class Meta:
        verbose_name = _("অর্ডার")
        verbose_name_plural = _("অর্ডারসমূহ")
    
    def __str__(self):
        return f"Order #{self.reference_no}"