import logging
from typing import Dict, Any
from .base_courier import BaseCourier
from ...schemas.shipment_request import ShipmentRequest
from ...schemas.shipment_response import ShipmentResponse
from ..http_clients.dhl_client import DHLHttpClient
from ..mapping.dhl.dhl_payload_builder import DHLPayloadBuilder
from ..mapping.dhl.dhl_response_mapper import DHLResponseMapper
from ..mapping.dhl.dhl_label_response_parser import DHLLabelResponseParser

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
    
    def fetch_label(self, courier_external_id: str) -> Dict[str, Any]:
        """
        Fetch label from DHL API.
        
        Args:
            courier_external_id: The courier external ID
            
        Returns:
            Dict containing label data or error
        """
        try:
            logger.info(f"DHL: Fetching label for shipment {courier_external_id}")
            
            # Use dedicated get_label method
            response = self.http_client.get_label(courier_external_id)
            
            if response.get('success') and response.get('data'):
                # Parse successful response using dedicated parser
                label_data = DHLLabelResponseParser.parse_success_response(response['data'])
                if label_data:
                    return label_data
                else:
                    return {
                        'success': False,
                        'error': 'Label URL not found in DHL response',
                        'error_code': 'LABEL_URL_NOT_FOUND'
                    }
            else:
                # Parse error response using dedicated parser
                error_info = DHLLabelResponseParser.parse_error_response(
                    response.get('error', 'Failed to fetch label from DHL')
                )
                return {
                    'success': False,
                    'error': error_info['error_message'],
                    'error_code': error_info['error_code']
                }
                
        except Exception as e:
            logger.error(f"DHL: Error fetching label: {str(e)}")
            return {
                'success': False,
                'error': f'DHL API error: {str(e)}',
                'error_code': 'COURIER_API_ERROR'
            }