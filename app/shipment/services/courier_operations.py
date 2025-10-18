import logging
from .courier_factory import courier_factory
from .courier_interface import CourierRequest, CourierResponse

logger = logging.getLogger(__name__)


class CourierOperations:
    """Service class for courier operations like creating shipments."""
    
    def create_shipment_with_courier(self, courier, request_data):
        """Create shipment with the specified courier."""
        logger.info(f"CourierOperations: Starting shipment creation with courier '{courier.name}'")
        try:
            # Convert request_data to CourierRequest format
            logger.info(f"CourierOperations: Converting request data to CourierRequest format")
            courier_request = CourierRequest(
                shipment_type=request_data.get('shipment_type', 'standard'),
                origin=request_data.get('origin', ''),
                destination=request_data.get('destination', ''),
                weight=request_data.get('weight', 0.0),
                dimensions=request_data.get('dimensions', {}),
                items=request_data.get('items', []),
                pickup_date=request_data.get('pickup_date', ''),
                special_instructions=request_data.get('special_instructions', ''),
                reference_number=request_data.get('reference_number', '')
            )
            logger.info(f"CourierOperations: CourierRequest created - origin='{courier_request.origin}', destination='{courier_request.destination}', weight={courier_request.weight}")
            
            # Create shipment using courier factory
            logger.info(f"CourierOperations: Calling courier_factory.create_shipment for '{courier.name.lower()}'")
            response = courier_factory.create_shipment(courier.name.lower(), courier_request)
            logger.info(f"CourierOperations: Received response from courier_factory: success={response.success}")
            
            return response
            
        except Exception as e:
            logger.error(f'Error creating shipment with courier: {str(e)}')
            return CourierResponse(
                success=False,
                error_message=f"Failed to create shipment: {str(e)}"
            )
