from django.urls import path
from .views import (
    ProductListView, ProductListView,
    ProductDetailView, checkout,
    order_detail, search
)

app_name = 'store'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('checkout/<int:product_id>/', checkout, name='checkout'),
    path('order/<str:ref_no>/', order_detail, name='order_detail'),
    path('search/', search, name='search'),
]