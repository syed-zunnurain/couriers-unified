import logging
from django.utils import timezone
from django.db import transaction
from shipment.models import ShipmentRequest
from .find_available_courier import FindAvailableCourier

logger = logging.getLogger(__name__)


class ShipmentProcessor:
    """Service class for processing shipment requests."""
    
    def __init__(self):
        self.max_retries = 3
        self.find_available_courier = FindAvailableCourier()
    
    def process_requests(self, batch_size=10):
        """Process a batch of shipment requests."""
        requests_to_process = self.get_requests_to_process(batch_size)
        
        results = {
            'total': len(requests_to_process),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for request in requests_to_process:
            try:
                result = self.process_single_request(request)
                results['details'].append(result)
                
                if result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                logger.error(f'Error processing request {request.id}: {str(e)}')
                results['failed'] += 1
                results['details'].append({
                    'request_id': request.id,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_requests_to_process(self, batch_size):
        """Get shipment requests that need processing."""
        return ShipmentRequest.objects.filter(
            status__in=['pending', 'failed'],
            retries__lt=self.max_retries
        ).order_by('created_at')[:batch_size]
    
    def process_single_request(self, request):
        """Process a single shipment request."""
        with transaction.atomic():
            # Update retry count and status
            request.retries += 1
            request.last_retried_at = timezone.now()
            request.status = 'processing'
            request.save()
            
            # Get request data
            request_data = request.request_body
            
            # Find available courier
            courier = self.find_available_courier.find(
                request_data.get('shipment_type_id'),
                request_data.get('route_id')
            )
            
            if not courier:
                request.status = 'failed'
                request.save()
                return {
                    'request_id': request.id,
                    'reference_number': request.reference_number,
                    'success': False,
                    'error': 'No available couriers for this shipment',
                    'courier': None
                }
            
            # Process with courier
            processing_result = self.process_with_courier(request_data, courier)
            
            if processing_result['success']:
                request.status = 'completed'
                request.save()
                return {
                    'request_id': request.id,
                    'reference_number': request.reference_number,
                    'success': True,
                    'message': processing_result['message'],
                    'courier': courier.name
                }
            else:
                request.status = 'failed'
                request.save()
                return {
                    'request_id': request.id,
                    'reference_number': request.reference_number,
                    'success': False,
                    'error': processing_result['error'],
                    'courier': courier.name
                }
    
    
    def process_with_courier(self, request_data, courier):
        """Process the shipment with the assigned courier."""
        # This is where you would integrate with actual courier APIs
        # For now, we'll simulate the processing
        return self.simulate_courier_processing(request_data, courier)
    
    def simulate_courier_processing(self, request_data, courier):
        """Simulate courier API processing."""
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
