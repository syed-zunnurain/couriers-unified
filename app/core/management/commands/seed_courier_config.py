import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Courier, CourierConfig

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seeds courier configurations for DHL, FedEx, and UPS'

    def handle(self, *args, **options):
        self.stdout.write('Starting to seed courier configurations...')

        # Define courier configurations
        courier_configs = [
            {
                'name': 'DHL',
                'config': {
                    'base_url': 'https://api-sandbox.dhl.com',
                    'api_key': 'jOE9bVeBIKVZAOI7hLdU2dNRdxNwDhBT',
                    'api_secret': 'FJ4miwlowXTsRPog',
                    'username': 'user-valid',
                    'password': 'SandboxPasswort2023!',
                    'is_active': True
                }
            }
        ]

        try:
            with transaction.atomic():
                for courier_data in courier_configs:
                    # Get or create courier
                    courier, created = Courier.objects.get_or_create(
                        name=courier_data['name'],
                        defaults={
                            'supports_cancellation': True, 
                            'is_active': True
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'Created {courier_data["name"]} courier')
                    else:
                        self.stdout.write(f'{courier_data["name"]} courier already exists')

                    # Create or update courier configuration
                    config, config_created = CourierConfig.objects.get_or_create(
                        courier=courier,
                        defaults=courier_data['config']
                    )
                    
                    if config_created:
                        self.stdout.write(f'Created {courier_data["name"]} courier configuration')
                    else:
                        self.stdout.write(f'{courier_data["name"]} courier configuration already exists')

            self.stdout.write(self.style.SUCCESS('Courier configurations seeding completed successfully!'))

        except Exception as e:
            logger.error(f"Error during courier configurations seeding: {e}")
            self.stdout.write(self.style.ERROR(f'Error during courier configurations seeding: {e}'))
