import logging
from typing import Optional
from django.db import transaction
from core.models import Courier
from ...models import Shipment
from ...repositories.repository_factory import repositories
from ...schemas.shipment_request import ShipmentRequest
from ...schemas.shipment_response import ShipmentResponse
from ..status.shipment_status_service import ShipmentStatusService

logger = logging.getLogger(__name__)


class ShipmentCreationService:
    def __init__(self, courier_factory_instance=None):
        self._courier_factory = courier_factory_instance
        self._find_courier = None
    
    def create_shipment(self, request: ShipmentRequest, shipment_type_id: int) -> ShipmentResponse:
        try:
            logger.info(f"ShipmentCreationService: Creating shipment for reference {request.reference_number}")
            
            # Lazy imports to avoid circular dependency
            if not self._courier_factory:
                from ..couriers.courier_factory import courier_factory
                self._courier_factory = courier_factory
            
            if not self._find_courier:
                from ..couriers.find_available_courier import FindAvailableCourier
                self._find_courier = FindAvailableCourier()
            
            courier = self._find_courier.find(shipment_type_id, request.shipper.city, request.consignee.city)
            if not courier:
                return ShipmentResponse.create_error_response(
                    'No available courier found for this route',
                    'NO_COURIER_AVAILABLE'
                )
            
            logger.info(f"ShipmentCreationService: Selected courier {courier.name} for shipment")
            
            courier_response = self._courier_factory.create_shipment(
                courier_name=courier.name.lower(),
                request=request,
                courier_obj=courier,
                shipment_type_id=shipment_type_id
            )
            
            if not courier_response.success:
                logger.error(f"ShipmentCreationService: Courier API failed: {courier_response.error_message}")
                return courier_response
            
            shipment = self._persist_shipment(request, courier_response, courier, shipment_type_id)
            
            ShipmentStatusService.create_status(
                shipment=shipment,
                status='created',
                address=f"{request.shipper.address}, {request.shipper.city}",
                postal_code=request.shipper.postal_code,
                country=request.shipper.country
            )
            
            logger.info(f"ShipmentCreationService: Successfully created shipment {shipment.id}")
            return courier_response
            
        except Exception as e:
            logger.error(f"ShipmentCreationService: Error creating shipment: {str(e)}")
            return ShipmentResponse.create_error_response(
                f'Error creating shipment: {str(e)}',
                'SHIPMENT_CREATION_ERROR'
            )
    
    def _persist_shipment(self, request: ShipmentRequest, response: ShipmentResponse, courier: Courier, shipment_type_id: int) -> Shipment:
        try:
            with transaction.atomic():
                shipment_type = repositories.shipment_type.get_by_id(shipment_type_id)
                if not shipment_type:
                    raise ValueError(f"ShipmentType with id {shipment_type_id} not found")
                
                shipment = repositories.shipment.create_shipment(
                    courier_id=courier.id,
                    shipment_type_id=shipment_type.id,
                    courier_external_id=response.tracking_number,
                    reference_number=request.reference_number,
                    shipper_id=request.shipper.id,
                    route_id=request.route.id,
                    consignee_id=request.consignee.id,
                    height=request.dimensions.height,
                    width=request.dimensions.width,
                    length=request.dimensions.length,
                    dimension_unit=request.dimensions.unit,
                    weight=request.weight.value,
                    weight_unit=request.weight.unit
                )
                
                logger.info(f"ShipmentCreationService: Persisted shipment {shipment.id} to database")
                return shipment
                
        except Exception as e:
            logger.error(f"ShipmentCreationService: Error persisting shipment: {str(e)}")
            raise
