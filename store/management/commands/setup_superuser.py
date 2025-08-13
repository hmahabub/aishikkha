# management/commands/setup_superuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Setup superuser'

    def handle(self, *args, **options):
        # Create superuser if doesn't exist
        if not User.objects.filter(username='aishhhiika').exists():
            User.objects.create_superuser('aishhhiika', 'admin@aishikkha.com', 'dhFh37F#a')
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin/admin123')
            )