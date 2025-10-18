import logging
from django.utils import timezone
from django.db import transaction
from shipment.models import ShipmentRequest, Shipper, Consignee
from core.models import Route
from .find_available_courier import FindAvailableCourier
from .courier_factory import courier_factory
from .courier_interface import CourierRequest, Weight, Dimensions

logger = logging.getLogger(__name__)


class ShipmentProcessor:
    """Service class for processing shipment requests."""
    
    def __init__(self):
        self.max_retries = 3
        self.find_available_courier = FindAvailableCourier()
    
    def process_requests(self, batch_size=10):
        """Process a batch of shipment requests."""
        logger.info(f"ShipmentProcessor: Starting to process requests with batch_size={batch_size}")
        requests_to_process = self.get_requests_to_process(batch_size)
        logger.info(f"ShipmentProcessor: Found {len(requests_to_process)} requests to process")
        
        results = {
            'total': len(requests_to_process),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for request in requests_to_process:
            logger.info(f"ShipmentProcessor: Processing request ID={request.id}, reference={request.reference_number}")
            try:
                result = self.process_single_request(request)
                results['details'].append(result)
                
                if result['success']:
                    results['successful'] += 1
                    logger.info(f"ShipmentProcessor: Successfully processed request ID={request.id}")
                else:
                    results['failed'] += 1
                    logger.warning(f"ShipmentProcessor: Failed to process request ID={request.id}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f'ShipmentProcessor: Error processing request {request.id}: {str(e)}')
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
        logger.info(f"ShipmentProcessor: Starting to process single request ID={request.id}")
        with transaction.atomic():
            request.retries += 1
            request.last_retried_at = timezone.now()
            request.status = 'processing'
            request.save()
            logger.info(f"ShipmentProcessor: Updated request ID={request.id} status to processing, retries={request.retries}")
            
            request_data = request.request_body
            logger.info(f"ShipmentProcessor: Request data for ID={request.id}: shipment_type_id={request_data.get('shipment_type_id')}")
            
            # Get shipper and consignee cities

            consignee = Consignee.objects.get(id=request_data.get('consignee_id'))
            shipper = Shipper.objects.get(id=request_data.get('shipper_id'))
            
            logger.info(f"ShipmentProcessor: Looking for available courier for request ID={request.id}")
            courier = self.find_available_courier.find(
                request_data.get('shipment_type_id'),
                shipper.city,
                consignee.city
            )
            
            if not courier:
                logger.warning(f"ShipmentProcessor: No available courier found for request ID={request.id}")
                request.status = 'failed'
                request.failed_reason = 'No available couriers for this shipment'
                request.save()
                return {
                    'request_id': request.id,
                    'reference_number': request.reference_number,
                    'success': False,
                    'error': 'No available couriers for this shipment',
                    'courier': None
                }
            
            logger.info(f"ShipmentProcessor: Found courier '{courier.name}' for request ID={request.id}")
            logger.info(f"ShipmentProcessor: Starting courier processing for request ID={request.id} with courier '{courier.name}'")
            processing_result = self.process_with_courier(request_data, request.reference_number, courier, shipper, consignee)
            
            if processing_result['success']:
                logger.info(f"ShipmentProcessor: Successfully processed request ID={request.id} with courier '{courier.name}'")
                request.failed_reason = None
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
                logger.warning(f"ShipmentProcessor: Failed to process request ID={request.id} with courier '{courier.name}': {processing_result.get('error', 'Unknown error')}")
                request.status = 'failed'
                request.failed_reason = processing_result.get('error', 'Unknown error')
                request.save()
                return {
                    'request_id': request.id,
                    'reference_number': request.reference_number,
                    'success': False,
                    'error': processing_result['error'],
                    'courier': courier.name
                }
    
    
    def process_with_courier(self, request_data, reference_number, courier, shipper, consignee):
        """Process the shipment with the assigned courier."""
        logger.info(f"ShipmentProcessor: Converting request data to CourierRequest format for courier '{courier.name}'")
        try:
            # Get or create the required objects
            consignee_city = consignee.city
            shipper_city = shipper.city
            
            # Get or create route
            route, created = Route.objects.get_or_create(
                origin=shipper_city,
                destination=consignee_city
            )
            
            # Create Weight and Dimensions objects
            weight = Weight(
                value=request_data.get('weight', 0.0),
                unit=request_data.get('weight_unit', 'kg')
            )
            
            dimensions_data = request_data.get('dimensions', {})
            dimensions = Dimensions(
                height=dimensions_data.get('height', 0.0),
                width=dimensions_data.get('width', 0.0),
                length=dimensions_data.get('length', 0.0),
                unit=request_data.get('dimension_unit', 'cm')
            )
            
            courier_request = CourierRequest(
                shipment_type=request_data.get('shipment_type', 'standard'),
                reference_number=reference_number,
                shipper=shipper,
                consignee=consignee,
                route=route,
                weight=weight,
                dimensions=dimensions,
                pickup_date=request_data.get('pickup_date'),
                special_instructions=request_data.get('special_instructions')
            )

            logger.info(f"ShipmentProcessor: Calling courier_factory.create_shipment for '{courier.name.lower()}'")
            courier_response = courier_factory.create_shipment(courier.name.lower(), courier_request)
            logger.info(f"ShipmentProcessor: Received response from courier_factory: success={courier_response.success}")
            
            if courier_response.success:
                logger.info(f"ShipmentProcessor: Courier '{courier.name}' processing successful, tracking_number={courier_response.tracking_number}")
                return {
                    'success': True,
                    'message': f'Successfully submitted to {courier.name}',
                    'tracking_number': courier_response.tracking_number,
                    'courier_reference': courier_response.courier_reference
                }
            else:
                logger.warning(f"ShipmentProcessor: Courier '{courier.name}' processing failed: {courier_response.error_message}")
                return {
                    'success': False,
                    'error': courier_response.error_message
                }
                
        except Exception as e:
            logger.error(f'ShipmentProcessor: Error creating shipment with courier: {str(e)}')
            return {
                'success': False,
                'error': f"Failed to create shipment: {str(e)}"
            }

    
    def simulate_courier_processing(self, request_data, courier):
        """Simulate courier API processing."""
        import random
        
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
