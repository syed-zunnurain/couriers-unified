import logging
from django.core.management.base import BaseCommand
from shipment.services.shipments.shipment_processor import ShipmentProcessor

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Worker command to process pending and failed shipment requests with retries < 3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        
        self.stdout.write('Starting shipment request processing...')
        logger.info(f"ShipmentWorker: Starting processing with batch_size={batch_size}")
        
        processor = ShipmentProcessor()
        logger.info("ShipmentWorker: Created ShipmentProcessor instance")
        results = processor.process_requests(batch_size)
        logger.info(f"ShipmentWorker: Processing completed with {results['total']} requests")
        
        if results['total'] == 0:
            self.stdout.write(self.style.SUCCESS('No shipment requests to process'))
            return
        
        self.stdout.write(f'Found {results["total"]} requests to process')
        
        for detail in results['details']:
            if detail['success']:
                courier_info = f" - Courier: {detail['courier']}" if detail.get('courier') else ""
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Processed request {detail["request_id"]} - {detail["reference_number"]}{courier_info}'
                    )
                )
            else:
                courier_info = f" - Courier: {detail['courier']}" if detail.get('courier') else ""
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed request {detail["request_id"]} - {detail["reference_number"]}{courier_info} - Error: {detail["error"]}'
                    )
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Processing Summary:')
        self.stdout.write(f'  Total processed: {results["total"]}')
        self.stdout.write(f'  Successful: {results["successful"]}')
        self.stdout.write(f'  Failed: {results["failed"]}')
        self.stdout.write('='*50)