from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order, Review

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

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'rating', 'title', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'আপনার নাম'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'আপনার ইমেইল'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'রিভিউ শিরোনাম'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'আপনার বিস্তারিত মতামত লিখুন...'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [
            ('', 'রেটিং নির্বাচন করুন'),
            (5, '৫ স্টার - চমৎকার'),
            (4, '৪ স্টার - ভালো'),
            (3, '৩ স্টার - মোটামুটি'),
            (2, '২ স্টার - খারাপ'),
            (1, '১ স্টার - অত্যন্ত খারাপ'),
        ]
        
        # Make all fields required
        for field in self.fields:
            self.fields[field].required = True