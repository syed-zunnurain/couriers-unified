import logging
from django.db import transaction
from shipment.models import Shipment
from core.models import Courier, ShipmentType
from ..couriers.courier_interface import CourierRequest, CourierResponse
from ...repositories.repository_factory import repositories

logger = logging.getLogger(__name__)


class ShipmentPersistenceService:
    """Service for persisting shipment data to the database using repository pattern."""
    
    def __init__(self):
        self._shipment_repo = repositories.shipment
        self._shipment_type_repo = repositories.shipment_type
    
    def update_shipment_with_tracking(
        self,
        shipment: Shipment,
        courier_response: CourierResponse
    ) -> Shipment:
        """
        Update shipment with tracking information from courier response.
        
        Args:
            shipment: The shipment to update
            courier_response: The response from the courier
            
        Returns:
            Updated Shipment object
        """
        try:
            with transaction.atomic():
                update_data = {}
                
                # Update tracking information if available
                if courier_response.tracking_number:
                    update_data['courier_external_id'] = courier_response.tracking_number
                
                # Add any additional fields that might be available
                if hasattr(shipment, 'tracking_number'):
                    update_data['tracking_number'] = courier_response.tracking_number
                
                if hasattr(shipment, 'estimated_delivery') and courier_response.estimated_delivery:
                    update_data['estimated_delivery'] = courier_response.estimated_delivery
                
                if hasattr(shipment, 'cost') and courier_response.cost:
                    update_data['cost'] = courier_response.cost
                
                updated_shipment = self._shipment_repo.update(shipment.id, **update_data)
                
                if updated_shipment:
                    logger.info(f"ShipmentPersistenceService: Updated shipment {shipment.id} with tracking info")
                    return updated_shipment
                else:
                    logger.error(f"ShipmentPersistenceService: Failed to update shipment {shipment.id}")
                    return shipment
                
        except Exception as e:
            logger.error(f"ShipmentPersistenceService: Error updating shipment: {str(e)}")
            raise
    
    def create_shipment(
        self,
        courier_request: CourierRequest,
        courier_response: CourierResponse,
        courier: Courier,
        shipment_type_id: int
    ) -> Shipment:
        """
        Create a new shipment. Throws IntegrityError if reference number already exists.
        
        Args:
            courier_request: The original courier request
            courier_response: The response from the courier
            courier: The courier object
            shipment_type_id: The shipment type ID
            
        Returns:
            Created Shipment object
            
        Raises:
            IntegrityError: If reference number already exists
        """
        try:
            with transaction.atomic():
                logger.info(f"ShipmentPersistenceService: Creating new shipment for reference {courier_request.reference_number}")
                
                # Get shipment type by ID using repository
                shipment_type = self._shipment_type_repo.get_by_id(shipment_type_id)
                if not shipment_type:
                    raise ValueError(f"ShipmentType with id {shipment_type_id} not found")
                
                # Create the shipment record using repository
                shipment = self._shipment_repo.create_shipment(
                    courier_id=courier.id,
                    shipment_type_id=shipment_type_id,
                    courier_external_id=courier_response.courier_reference or '',
                    reference_number=courier_request.reference_number,
                    shipper_id=courier_request.shipper.id,
                    route_id=courier_request.route.id,
                    consignee_id=courier_request.consignee.id,
                    height=courier_request.dimensions.height,
                    width=courier_request.dimensions.width,
                    length=courier_request.dimensions.length,
                    dimension_unit=courier_request.dimensions.unit,
                    weight=courier_request.weight.value,
                    weight_unit=courier_request.weight.unit
                )
                
                logger.info(f"ShipmentPersistenceService: Created shipment {shipment.id} for reference {courier_request.reference_number}")
                return shipment
                
        except Exception as e:
            logger.error(f"ShipmentPersistenceService: Error creating shipment: {str(e)}")
            raise
