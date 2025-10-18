import logging
from django.db import transaction
from shipment.models import Shipment
from core.models import Courier, ShipmentType
from .courier_interface import CourierRequest, CourierResponse

logger = logging.getLogger(__name__)


class ShipmentPersistenceService:
    """Service for persisting shipment data to the database."""
    
    @staticmethod
    def update_shipment_with_tracking(
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
                # Update tracking information if available
                if courier_response.tracking_number:
                    shipment.courier_external_id = courier_response.tracking_number
                
                # Add any additional fields that might be available
                if hasattr(shipment, 'tracking_number'):
                    shipment.tracking_number = courier_response.tracking_number
                
                if hasattr(shipment, 'estimated_delivery') and courier_response.estimated_delivery:
                    shipment.estimated_delivery = courier_response.estimated_delivery
                
                if hasattr(shipment, 'cost') and courier_response.cost:
                    shipment.cost = courier_response.cost
                
                shipment.save()
                
                logger.info(f"ShipmentPersistenceService: Updated shipment {shipment.id} with tracking info")
                return shipment
                
        except Exception as e:
            logger.error(f"ShipmentPersistenceService: Error updating shipment: {str(e)}")
            raise
    
    @staticmethod
    def create_shipment(
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
                
                # Get shipment type by ID
                shipment_type = ShipmentType.objects.get(id=shipment_type_id)
                
                # Create the shipment record
                shipment = Shipment.objects.create(
                    courier=courier,
                    shipment_type=shipment_type,
                    courier_external_id=courier_response.courier_reference or '',
                    reference_number=courier_request.reference_number,
                    shipper=courier_request.shipper,
                    route=courier_request.route,
                    consignee=courier_request.consignee,
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
