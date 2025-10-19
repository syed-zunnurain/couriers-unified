import logging
from typing import Dict, Any
from .base_courier import BaseCourier
from ...schemas.shipment_request import ShipmentRequest
from ...schemas.shipment_response import ShipmentResponse
from ..http_clients.dhl_client import DHLHttpClient
from ..mapping.dhl.dhl_payload_builder import DHLPayloadBuilder
from ..mapping.dhl.dhl_response_mapper import DHLResponseMapper

logger = logging.getLogger(__name__)


class DHLCourier(BaseCourier):
    """DHL courier implementation following SOLID principles."""
    
    def _create_http_client(self):
        """Create DHL HTTP client with OAuth credentials."""
        return DHLHttpClient(
            base_url=self.config.get('base_url', ''),
            api_key=self.config.get('api_key'),
            api_secret=self.config.get('api_secret'),
            username=self.config.get('username'),
            password=self.config.get('password'),
            timeout=30
        )
    
    def _prepare_payload(self, request: ShipmentRequest) -> Dict[str, Any]:
        """Prepare DHL-specific payload from standardized request."""
        return DHLPayloadBuilder.build_dhl_payload(request)
    
    def _map_response(self, response_data: Dict[str, Any]) -> ShipmentResponse:
        """Map DHL response to standardized ShipmentResponse."""
        return DHLResponseMapper.map_dhl_response_to_shipment_response(
            response_data.get('data', {}),
            response_data.get('success', False)
        )