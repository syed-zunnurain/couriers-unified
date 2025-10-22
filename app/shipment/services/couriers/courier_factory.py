import logging
from typing import Dict, Any, Optional
from .courier_dtos import CourierRequest, CourierResponse
from .dhl_courier import DHLCourier
from .base_courier import BaseCourier
from ...repositories.repository_factory import repositories
from ...schemas.tracking_response import TrackingResponse
from ...schemas.label_response import LabelResponse

logger = logging.getLogger(__name__)


class CourierFactory:
    COURIER_CLASSES = {
        'dhl': DHLCourier,
    }
    
    def __init__(self):
        self._couriers: Dict[str, BaseCourier] = {}
    
    def get_courier_instance(self, courier_name: str, courier_obj=None) -> Optional[BaseCourier]:
        courier_name = courier_name.lower()
        logger.info(f"CourierFactory: Getting courier instance for '{courier_name}'")
        
        if courier_name not in self.COURIER_CLASSES:
            logger.warning(f"CourierFactory: Courier '{courier_name}' not found in COURIER_CLASSES")
            return None

        try:
            logger.info(f"CourierFactory: Looking up courier configuration for '{courier_name}' in database")
            courier_config = repositories.courier_config.get_by_courier_name(courier_name)
            if not courier_config:
                return None
            logger.info(f"CourierFactory: Found courier configuration for '{courier_name}'")
            
            if not courier_obj:
                courier_obj = courier_config.courier
                
        except Exception as e:
            logger.error(f"CourierFactory: Error getting courier config: {str(e)}")
            return None
        
        courier_class = self.COURIER_CLASSES[courier_name]
        logger.info(f"CourierFactory: Creating {courier_class.__name__} instance for '{courier_name}'")
        config = {
            'base_url': courier_config.base_url,
            'api_key': courier_config.api_key,
            'api_secret': courier_config.api_secret,
            'username': courier_config.username,
            'password': courier_config.password,
        }
        logger.info(f"CourierFactory: Configuration loaded - base_url={config['base_url']}")
        
        courier_instance = courier_class(courier_name, config, courier_obj)
        logger.info(f"CourierFactory: Created courier instance: {courier_instance}")
        return courier_instance
    
    def create_shipment(self, courier_name: str, request: CourierRequest, courier_obj=None, shipment_type_id: int = None) -> CourierResponse:
        logger.info(f"CourierFactory: Creating shipment with courier '{courier_name}'")
        try:
            logger.info(f"CourierFactory: Getting courier instance for '{courier_name}'")
            courier = self.get_courier_instance(courier_name, courier_obj)
            if not courier:
                logger.error(f"CourierFactory: Courier '{courier_name}' not found or not configured")
                return CourierResponse(
                    success=False,
                    error_message=f"Courier '{courier_name}' not found or not configured"
                )
            
            logger.info(f"CourierFactory: Found courier instance '{courier.courier_name}', calling create_shipment")
            response = courier.create_shipment(request, shipment_type_id)
            logger.info(f"CourierFactory: Received response from courier: success={response.success}")
            return response
        except Exception as e:
            return CourierResponse(
                success=False,
                error_message=f"Failed to create shipment with {courier_name}: {str(e)}"
            )
    
    def fetch_label(self, courier_name: str, courier_external_id: str) -> LabelResponse:
        logger.info(f"CourierFactory: Fetching label with courier '{courier_name}'")
        try:
            logger.info(f"CourierFactory: Getting courier instance for '{courier_name}'")
            courier = self.get_courier_instance(courier_name)
            if not courier:
                logger.error(f"CourierFactory: Courier '{courier_name}' not found or not configured")
                return LabelResponse.create_error_response(
                    f"Courier '{courier_name}' not found or not configured",
                    'COURIER_NOT_FOUND'
                )
            
            logger.info(f"CourierFactory: Found courier instance '{courier.courier_name}', calling fetch_label")
            response = courier.fetch_label(courier_external_id)
            logger.info(f"CourierFactory: Received response from courier: success={response.success}")
            return response
        except Exception as e:
            return LabelResponse.create_error_response(
                f"Failed to fetch label with {courier_name}: {str(e)}",
                'COURIER_API_ERROR'
            )
    
    def track_shipment(self, courier_name: str, courier_external_id: str) -> TrackingResponse:
        logger.info(f"CourierFactory: Tracking shipment with courier '{courier_name}'")
        try:
            logger.info(f"CourierFactory: Getting courier instance for '{courier_name}'")
            courier = self.get_courier_instance(courier_name)
            if not courier:
                logger.error(f"CourierFactory: Courier '{courier_name}' not found or not configured")
                return TrackingResponse.create_error_response(
                    f"Courier '{courier_name}' not found or not configured",
                    'COURIER_NOT_FOUND'
                )
            
            logger.info(f"CourierFactory: Found courier instance '{courier.courier_name}', calling track_shipment")
            response = courier.track_shipment(courier_external_id)
            logger.info(f"CourierFactory: Received response from courier: success={response.success}")
            return response
        except Exception as e:
            return TrackingResponse.create_error_response(
                f"Failed to track shipment with {courier_name}: {str(e)}",
                'COURIER_API_ERROR'
            )
    
    def get_available_couriers(self) -> list:
        return [config.courier.name for config in repositories.courier_config.get_active_configs()]


courier_factory = CourierFactory()
