from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random
import string
from django.db.models import Q

from .models import Product, Category, Order
from .forms import OrderForm

class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

def checkout(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Generate random reference number
            ref_no = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            
            order = form.save(commit=False)
            order.product = product
            order.reference_no = ref_no
            order.save()
            
            # Send email with reference number
            send_mail(
                _('আপনার অর্ডার রেফারেন্স নম্বর'),
                _('আপনার অর্ডারের রেফারেন্স নম্বর: {}। পেমেন্ট সম্পন্ন হলে আমরা আপনাকে জানাবো।').format(ref_no),
                settings.DEFAULT_FROM_EMAIL,
                [order.email],
                fail_silently=False,
            )
            
            return redirect('order_detail', ref_no=ref_no)
    else:
        form = OrderForm()
    
    return render(request, 'store/checkout.html', {
        'product': product,
        'form': form,
    })

def order_detail(request, ref_no):
    order = get_object_or_404(Order, reference_no=ref_no)
    return render(request, 'store/order_detail.html', {'order': order})

def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    else:
        products = Product.objects.none()
    
    return render(request, 'store/search_results.html', {
        'products': products,
        'query': query,
        'categories': Category.objects.all(),  # Include categories for sidebar
    })