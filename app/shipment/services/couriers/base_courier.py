import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ...schemas.shipment_request import ShipmentRequest
from ...schemas.shipment_response import ShipmentResponse
from ...schemas.tracking_response import TrackingResponse

logger = logging.getLogger(__name__)


class BaseCourier(ABC):
    def __init__(self, courier_name: str, config: Dict[str, Any], courier_obj=None):
        self.courier_name = courier_name
        self.config = config
        self.courier_obj = courier_obj
        self.http_client = self._create_http_client()
    
    @abstractmethod
    def _create_http_client(self):
        pass
    
    @abstractmethod
    def _prepare_payload(self, request: ShipmentRequest) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def _map_response(self, response_data: Dict[str, Any]) -> ShipmentResponse:
        pass
    
    @abstractmethod
    def fetch_label(self, courier_external_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def track_shipment(self, courier_external_id: str) -> TrackingResponse:
        pass
    
    def create_shipment(self, request: ShipmentRequest, shipment_type_id: int = None) -> ShipmentResponse:
        try:
            logger.info(f"{self.courier_name}: Starting shipment creation")
            logger.info(f"{self.courier_name}: Request details - Reference: {request.reference_number}, Weight: {request.weight.value} {request.weight.unit}, Dimensions: {request.dimensions.height}x{request.dimensions.width}x{request.dimensions.length} {request.dimensions.unit}, Shipper: {request.shipper.city}, Consignee: {request.consignee.city}")
            
            payload = self._prepare_payload(request)
            logger.info(f"{self.courier_name}: Prepared payload")
            logger.debug(f"{self.courier_name}: Full payload: {payload}")
            
            response_data = self.http_client.create_shipment(payload)
            
            shipment_response = self._map_response(response_data)
            
            if shipment_response.success and self.courier_obj and shipment_type_id:
                self._persist_shipment(request, shipment_response, shipment_type_id)
            
            return shipment_response
            
        except Exception as e:
            logger.error(f"{self.courier_name}: Error creating shipment: {str(e)}")
            return ShipmentResponse(
                success=False,
                error_message=f"Courier error: {str(e)}"
            )
    
    def _persist_shipment(self, request: ShipmentRequest, response: ShipmentResponse, shipment_type_id: int):
        try:
            from ..shipments.shipment_creation_service import ShipmentCreationService
            shipment = ShipmentCreationService.create_shipment(
                request, response, self.courier_obj, shipment_type_id
            )
            logger.info(f"{self.courier_name}: Persisted shipment {shipment.id} to database")
        except Exception as e:
            logger.error(f"{self.courier_name}: Error persisting shipment: {str(e)}")
