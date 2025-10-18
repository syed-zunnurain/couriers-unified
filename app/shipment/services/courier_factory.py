import logging
from typing import Dict, Any, Optional
from .courier_interface import CourierInterface, CourierRequest, CourierResponse
from .couriers.dhl_courier import DHLCourier
from core.models import CourierConfig

logger = logging.getLogger(__name__)


class CourierFactory:
    """Factory class to create and manage courier instances."""
    
    COURIER_CLASSES = {
        'dhl': DHLCourier,
    }
    
    def __init__(self):
        self._couriers: Dict[str, CourierInterface] = {}
    
    def get_courier_instance(self, courier_name: str, courier_obj=None) -> Optional[CourierInterface]:
        """Get courier instance with configuration from database."""
        courier_name = courier_name.lower()
        logger.info(f"CourierFactory: Getting courier instance for '{courier_name}'")
        
        if courier_name not in self.COURIER_CLASSES:
            logger.warning(f"CourierFactory: Courier '{courier_name}' not found in COURIER_CLASSES")
            return None
        
        try:
            logger.info(f"CourierFactory: Looking up courier configuration for '{courier_name}' in database")
            courier_config = CourierConfig.objects.select_related('courier').get(
                courier__name__iexact=courier_name,
                is_active=True
            )
            logger.info(f"CourierFactory: Found courier configuration for '{courier_name}'")
        except CourierConfig.DoesNotExist:
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
        """Create shipment with specified courier."""
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
    
    def get_available_couriers(self) -> list:
        """Get list of available courier names from database."""
        return list(CourierConfig.objects.filter(is_active=True).values_list('courier__name', flat=True))


courier_factory = CourierFactory()
