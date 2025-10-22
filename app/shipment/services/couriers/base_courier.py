import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ...schemas.shipment_request import ShipmentRequest
from ...schemas.shipment_response import ShipmentResponse
from ...schemas.tracking_response import TrackingResponse
from ...schemas.label_response import LabelResponse

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
    def fetch_label(self, courier_external_id: str) -> LabelResponse:
        pass
    
    @abstractmethod
    def track_shipment(self, courier_external_id: str) -> TrackingResponse:
        pass
    
    @abstractmethod
    def create_shipment(self, request: ShipmentRequest, shipment_type_id: int = None) -> ShipmentResponse:
        pass
    
