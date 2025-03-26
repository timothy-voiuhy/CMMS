from django.core.management.base import BaseCommand
from django.db import transaction
from AppCmmsportals.models import User

class Command(BaseCommand):
    help = 'Create a CMMS superuser'

    def add_arguments(self, parser):
        parser.add_argument('--employee_id', required=True)
        parser.add_argument('--password', required=True)

    def handle(self, *args, **options):
        employee_id = options['employee_id']
        password = options['password']
        
        with transaction.atomic():
            if User.objects.filter(employee_id=employee_id).exists():
                self.stdout.write(self.style.WARNING(f'User {employee_id} already exists'))
                return
                
            user = User.objects.create_superuser(
                employee_id=employee_id,
                password=password
            )
            
            self.stdout.write(self.style.SUCCESS(f'Superuser {employee_id} created successfully')) 