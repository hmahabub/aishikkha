from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random
import string
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, FileResponse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .bkash_service import BkashService
import json
import logging



from .models import Product, Category, Order
from .forms import OrderForm

logger = logging.getLogger(__name__)

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



def checkout_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        customer_name = request.POST.get('name')
        phone = request.POST.get('phone', "")
        email = request.POST.get('email')
        if email:
            # Create order
            order = Order.objects.create(
                customer_name=customer_name,
                phone = phone,
                email=email,
                product=product,
                amount=product.price
            )
            return redirect('store:payment_page', order_id=order.id)
    
    return render(request, 'store/checkout.html', {'product': product, 'form': OrderForm})

def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.status == 'paid':
        return redirect('store:payment_success', order_id=order.id)
    
    context = {
        'order': order,
        'bkash_config': {
            'app_key': settings.BKASH_CONFIG['APP_KEY'],
            'is_sandbox': settings.BKASH_CONFIG['IS_SANDBOX']
        }
    }
    return render(request, 'store/payment.html', context)

@csrf_exempt
def create_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            order = get_object_or_404(Order, id=order_id)
            
            bkash_service = BkashService()
            payment_response = bkash_service.create_payment(
                amount=float(order.amount),
                invoice_number=str(order.id)
            )
            
            if payment_response and payment_response.get('statusCode') == '0000':
                order.bkash_payment_id = payment_response.get('paymentID')
                order.save()
                
                return JsonResponse({
                    'success': True,
                    'payment_id': payment_response.get('paymentID'),
                    'bkash_url': payment_response.get('bkashURL'), 
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to create payment'
                })
                
        except Exception as e:
            logger.error(f"Payment creation error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def execute_payment(request):
    if request.method == 'GET':
        try:
            payment_id = request.GET.get('paymentID')
            
            bkash_service = BkashService()
            execute_response = bkash_service.execute_payment(payment_id)
            
            if execute_response and execute_response.get('statusCode') == '0000':
                # Update order status
                try:
                    order = Order.objects.get(bkash_payment_id=payment_id)
                    order.status = 'paid'
                    order.trx_id = execute_response.get('trxID')
                    order.save()
                    
                    # Send email with download link
                    # send_ebook_email(order)
                    return redirect('store:payment_success', order_id=order.id)

                except Order.DoesNotExist:
                    return redirect('store:payment_failed', message= 'Order not found')

            else:
                return redirect('store:payment_failed', message= 'Payment execution failed')
                
        except Exception as e:
            logger.error(f"Payment execution error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def send_ebook_email(order):
    try:
        subject = f'Your eBook Purchase: {order.product.title}'
        download_link = f"http://aishikkha.com/download/{order.id}/"  # Update with your domain
        
        message = f"""
        Thank you for your purchase!
        
        Product: {order.product.title}
        Order ID: {order.id}
        Amount: {order.amount} BDT
        Transaction ID: {order.trx_id}
        
        Download your eBook here: {download_link}
        
        This link will be valid for 30 days.
        
        Thank you for your business!
        """
        print(subject,
            message,
            settings.EMAIL_HOST_USER,
            [order.email])
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [order.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")

def download_ebook(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'paid':
        return HttpResponse('Payment not confirmed', status=403)
    
    # Serve the file
    if order.product.pdf_file:
        response = FileResponse(
            order.product.pdf_file.open('rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=f"{order.product.title}.pdf"
        )
        return response
    
    return HttpResponse('File not found', status=404)

def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/payment_success.html', {'order': order})

def payment_failed(request, message):
    return render(request, 'store/payment_failed.html', {'message': message})

@csrf_exempt
def payment_callback(request):
    # Handle bKash callback (optional)
    payment_id = request.GET.get('paymentID')
            
    bkash_service = BkashService()
    execute_response = bkash_service.execute_payment(payment_id)
    if request.method == "POST":
        # Process callback data
        pass
    return HttpResponse('OK')
