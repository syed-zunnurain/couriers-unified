"""Service for processing shipments with couriers."""

import logging
from typing import Dict, Any
from .find_available_courier import FindAvailableCourier
# Lazy import to avoid circular dependency

logger = logging.getLogger(__name__)


class CourierProcessor:
    """Handles courier-specific processing following SRP."""
    
    def __init__(self, find_available_courier: FindAvailableCourier = None):
        self.find_available_courier = find_available_courier or FindAvailableCourier()
    
    def process_with_courier(self, request_data: Dict[str, Any], reference_number: str, shipper, consignee) -> Dict[str, Any]:
        """Process the shipment with the assigned courier."""
        logger.info(f"CourierProcessor: Looking for available courier")
        
        # Find available courier
        courier = self.find_available_courier.find(
            request_data.get('shipment_type_id'),
            shipper.city,
            consignee.city
        )
        
        if not courier:
            logger.warning(f"CourierProcessor: No available courier found")
            return {
                'success': False,
                'error': 'No available couriers for this shipment',
                'courier': None
            }
        
        logger.info(f"CourierProcessor: Found courier '{courier.name}'")
        return self._create_shipment_with_courier(request_data, reference_number, courier, shipper, consignee)
    
    def _create_shipment_with_courier(self, request_data: Dict[str, Any], reference_number: str, courier, shipper, consignee) -> Dict[str, Any]:
        """Create shipment with specific courier."""
        logger.info(f"CourierProcessor: Starting courier processing with courier '{courier.name}'")
        
        try:
            # Convert request data to courier format
            from ..requests.request_data_converter import RequestDataConverter
            data_converter = RequestDataConverter()
            courier_request = data_converter.convert_to_courier_request(
                request_data, reference_number, shipper, consignee
            )

            logger.info(f"CourierProcessor: Calling courier_factory.create_shipment for '{courier.name.lower()}'")
            logger.info(f"CourierProcessor: Request body details - Reference: {reference_number}, Weight: {courier_request.weight.value} {courier_request.weight.unit}, Dimensions: {courier_request.dimensions.height}x{courier_request.dimensions.width}x{courier_request.dimensions.length} {courier_request.dimensions.unit}, Shipper: {shipper.city}, Consignee: {consignee.city}")
            
            # Lazy import to avoid circular dependency
            from .courier_factory import courier_factory
            
            courier_response = courier_factory.create_shipment(
                courier.name.lower(), 
                courier_request, 
                courier, 
                request_data.get('shipment_type_id')
            )
            
            logger.info(f"CourierProcessor: Received response from courier_factory: success={courier_response.success}")
            
            if courier_response.success:
                logger.info(f"CourierProcessor: Courier '{courier.name}' processing successful, tracking_number={courier_response.tracking_number}")
                return {
                    'success': True,
                    'message': f'Successfully submitted to {courier.name}',
                    'tracking_number': courier_response.tracking_number,
                    'courier_reference': courier_response.courier_reference,
                    'courier': courier.name
                }
            else:
                logger.warning(f"CourierProcessor: Courier '{courier.name}' processing failed: {courier_response.error_message}")
                return {
                    'success': False,
                    'error': courier_response.error_message,
                    'courier': courier.name
                }
                
        except Exception as e:
            logger.error(f'CourierProcessor: Error creating shipment with courier: {str(e)}')
            return {
                'success': False,
                'error': f"Failed to create shipment: {str(e)}",
                'courier': courier.name
            }
