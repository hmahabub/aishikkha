from django.urls import path
from .views import *

app_name = 'store'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('product', ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('product/<int:id>/', product_detail, name='product_detail'),
    path('product/<int:id>/<slug:slug>/', product_detail, name='product_detail'),
    path('review/add/<int:product_id>/', add_review, name='add_review'),
    path('review/edit/<int:review_id>/', edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', delete_review, name='delete_review'),
    path('ajax/reviews/<int:product_id>/', get_reviews_ajax, name='get_reviews_ajax'),

    path('order/<str:ref_no>/', order_detail, name='order_detail'),
    path('search/', search, name='search'),
    path('checkout/<int:product_id>/', checkout_page, name='checkout'),
    path('payment/<uuid:order_id>/', payment_page, name='payment_page'),
    path('api/create-payment/', create_payment, name='create_payment'),
    path('api/execute-payment/', execute_payment, name='execute_payment'),
    path('download/<uuid:order_id>/', download_ebook, name='download_ebook'),
    path('payment/success/<uuid:order_id>/', payment_success, name='payment_success'),
    path('payment/callback/', execute_payment, name='payment_callback'),
]
