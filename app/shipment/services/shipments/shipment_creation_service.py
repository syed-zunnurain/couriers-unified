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
    @staticmethod
    def create_shipment(
        request: ShipmentRequest,
        response: ShipmentResponse,
        courier: Courier,
        shipment_type_id: int
    ) -> Shipment:
        try:
            with transaction.atomic():
                logger.info(f"ShipmentCreationService: Creating new shipment for reference {request.reference_number}")
                logger.info(f"ShipmentCreationService: Request details - Weight: {request.weight.value} {request.weight.unit}, Dimensions: {request.dimensions.height}x{request.dimensions.width}x{request.dimensions.length} {request.dimensions.unit}, Shipper: {request.shipper.city}, Consignee: {request.consignee.city}, Courier: {courier.name}")
                
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
                
                # Create initial "created" status
                ShipmentStatusService.create_status(
                    shipment=shipment,
                    status='created',
                    address=f"{request.shipper.address}, {request.shipper.city}",
                    postal_code=request.shipper.postal_code,
                    country=request.shipper.country
                )
                
                logger.info(f"ShipmentCreationService: Created shipment {shipment.id} for reference {request.reference_number}")
                logger.info(f"ShipmentCreationService: Created initial 'created' status for shipment {shipment.id}")
                return shipment
                
        except Exception as e:
            logger.error(f"ShipmentCreationService: Error creating shipment: {str(e)}")
            raise
