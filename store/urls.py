from django.urls import path
from .views import *

app_name = 'store'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('order/<str:ref_no>/', order_detail, name='order_detail'),
    path('search/', search, name='search'),
    path('checkout/<int:product_id>/', checkout_page, name='checkout'),
    path('payment/<uuid:order_id>/', payment_page, name='payment_page'),
    path('api/create-payment/', create_payment, name='create_payment'),
    path('api/execute-payment/', execute_payment, name='execute_payment'),
    path('download/<uuid:order_id>/', download_ebook, name='download_ebook'),
    path('payment/success/<uuid:order_id>/', payment_success, name='payment_success'),
    path('payment/callback/', payment_callback, name='payment_callback'),
]
