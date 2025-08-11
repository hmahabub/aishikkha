# management/commands/setup_bkash.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Product

class Command(BaseCommand):
    help = 'Setup initial data for bKash integration'

    def handle(self, *args, **options):
        # Create superuser if doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin/admin123')
            )

        # Create sample product
        if not Product.objects.exists():
            Product.objects.create(
                name='Sample eBook - Django Guide',
                price=500.00,
                download_link='https://example.com/sample-ebook.pdf'
            )
            self.stdout.write(
                self.style.SUCCESS('Created sample product')
            )

        self.stdout.write(
            self.style.SUCCESS('Setup completed successfully!')
        )