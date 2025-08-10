from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'email', 'phone']
        labels = {
            'customer_name': _('ক্রেতার নাম'),
            'email': _('ইমেইল ঠিকানা'),
            'phone': _('ফোন নম্বর'),
        }
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }