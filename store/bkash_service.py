import requests
import json
from django.conf import settings
from django.core.cache import cache

class BkashService:
    def __init__(self):
        self.config = settings.BKASH_CONFIG
        self.base_url = self.config['SANDBOX_BASE_URL'] if self.config['IS_SANDBOX'] else self.config['PRODUCTION_BASE_URL']
        self.website_url = self.config['WEB_URL']
    def get_token(self):
        # Check if token exists in cache
        token = cache.get('bkash_token')
        if token:
            return token
            
        url = f"{self.base_url}/tokenized/checkout/token/grant"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'username': self.config['USERNAME'],
            'password': self.config['PASSWORD']
        }
        data = {
            'app_key': self.config['APP_KEY'],
            'app_secret': self.config['APP_SECRET']
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('id_token')
            # Cache token for 50 minutes (expires in 1 hour)
            cache.set('bkash_token', token, 3000)
            return token
        return None
    
    def create_payment(self, amount, invoice_number, intent='sale'):
        token = self.get_token()
        if not token:
            return None
            
        url = f"{self.base_url}/tokenized/checkout/create"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authorization': token,
            'x-app-key': self.config['APP_KEY']
        }
        data = {
            'mode': '0011',
            'payerReference': invoice_number,
            'callbackURL': f"{self.website_url}/payment/callback/",  # Update with your domain
            'amount': str(amount),
            'currency': 'BDT',
            'intent': intent,
            'merchantInvoiceNumber': invoice_number
        }
        
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        if response.status_code == 200:
            return response.json()
        return None
    
    def execute_payment(self, payment_id):
        token = self.get_token()
        if not token:
            return None
            
        url = f"{self.base_url}/tokenized/checkout/execute"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authorization': token,
            'x-app-key': self.config['APP_KEY']
        }
        data = {
            'paymentID': payment_id
        }
        
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        if response.status_code == 200:
            return response.json()
        return None
    
    def query_payment(self, payment_id):
        token = self.get_token()
        if not token:
            return None
            
        url = f"{self.base_url}/tokenized/checkout/payment/status"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authorization': token,
            'x-app-key': self.config['APP_KEY']
        }
        data = {
            'paymentID': payment_id
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        return None
