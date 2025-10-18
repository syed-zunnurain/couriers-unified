import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from shipment.models import ShipmentRequest
from core.models import Courier, CourierShipmentType, CourierRoute

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process pending and failed shipment requests with retries < 3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of requests to process in one batch (default: 10)'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        
        self.stdout.write('Starting shipment request processing...')
        
        # Get requests to process
        requests_to_process = self.get_requests_to_process(batch_size)
        
        if not requests_to_process:
            self.stdout.write(self.style.SUCCESS('No shipment requests to process'))
            return
        
        self.stdout.write(f'Found {len(requests_to_process)} requests to process')
        
        # Process each request
        processed_count = 0
        success_count = 0
        failure_count = 0
        
        for request in requests_to_process:
            try:
                result = self.process_shipment_request(request)
                processed_count += 1
                
                if result['success']:
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Processed request {request.id} - {request.reference_number} - Status: {result["new_status"]}'
                        )
                    )
                else:
                    failure_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Failed to process request {request.id} - {request.reference_number} - Error: {result["error"]}'
                        )
                    )
                    
            except Exception as e:
                failure_count += 1
                logger.error(f'Error processing request {request.id}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'✗ Exception processing request {request.id}: {str(e)}')
                )
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Processing Summary:')
        self.stdout.write(f'  Total processed: {processed_count}')
        self.stdout.write(f'  Successful: {success_count}')
        self.stdout.write(f'  Failed: {failure_count}')
        self.stdout.write('='*50)

    def get_requests_to_process(self, batch_size):
        """Get shipment requests that need processing."""
        return ShipmentRequest.objects.filter(
            status__in=['pending', 'failed'],
            retries__lt=3
        ).order_by('created_at')[:batch_size]

    def process_shipment_request(self, request):
        """Process a single shipment request."""
        try:
            # Update retry count and last retried timestamp
            request.retries += 1
            request.last_retried_at = timezone.now()
            request.status = 'processing'
            request.save()
            
            # Get request data
            request_data = request.request_body
            
            # Validate courier availability
            available_couriers = self.get_available_couriers(request_data)
            
            if len(available_couriers) == 0:
                # Log no couriers available
                self.stdout.write(
                    self.style.ERROR(
                        f'  → No available couriers for shipment type {request_data.get("shipment_type_id")} and route {request_data.get("route_id")}'
                    )
                )
                # Mark as failed if no courier available
                request.status = 'failed'
                request.save()
                return {
                    'success': False,
                    'error': 'No available couriers for this shipment',
                    'new_status': 'failed'
                }

            first_available_courier = available_couriers.first()
            
            # Log the assigned courier
            self.stdout.write(
                self.style.WARNING(
                    f'  → Assigning courier: {first_available_courier.name} (ID: {first_available_courier.id})'
                )
            )
            
            # Simulate processing (in real implementation, this would call courier APIs)
            processing_result = self.simulate_courier_processing(request_data, first_available_courier)
            
            if processing_result['success']:
                request.status = 'completed'
                request.save()
                return {
                    'success': True,
                    'new_status': 'processing',
                    'message': processing_result['message']
                }
            else:
                request.status = 'failed'
                request.save()
                return {
                    'success': False,
                    'error': processing_result['error'],
                    'new_status': request.status
                }
                
        except Exception as e:
            request.retries += 1
            request.last_retried_at = timezone.now()
            if request.retries >= 3:
                request.status = 'failed'
            request.save()
            return {
                'success': False,
                'error': str(e),
                'new_status': request.status
            }

    def get_available_couriers(self, request_data):
        """Get available couriers for this shipment."""
        try:
            shipment_type_id = request_data.get('shipment_type_id')
            route_id = request_data.get('route_id')
            
            # Check if there's an active courier that supports this shipment type and route
            courier_shipment_types = CourierShipmentType.objects.filter(
                shipment_type_id=shipment_type_id,
                courier__is_active=True
            )
            
            courier_routes = CourierRoute.objects.filter(
                route_id=route_id,
                is_active=True,
                courier__is_active=True
            )
            
            # Find couriers that support both shipment type and route
            available_courier_ids = set()
            for cst in courier_shipment_types:
                for cr in courier_routes:
                    if cst.courier_id == cr.courier_id:
                        available_courier_ids.add(cst.courier_id)
            
            # Return Courier queryset for available couriers
            if available_courier_ids:
                return Courier.objects.filter(id__in=available_courier_ids)
            else:
                return Courier.objects.none()
            
        except Exception as e:
            logger.error(f'Error checking courier availability: {str(e)}')
            return Courier.objects.none()

    def simulate_courier_processing(self, request_data, courier):
        """Simulate courier API processing (replace with actual courier API calls)."""
        import random
        
        # Simulate 80% success rate
        if random.random() < 0.8:
            return {
                'success': True,
                'message': f'Successfully submitted to courier: {courier.name}'
            }
        else:
            return {
                'success': False,
                'error': f'Courier {courier.name} API temporarily unavailable'
            }
