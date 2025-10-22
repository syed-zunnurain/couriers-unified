import logging
from typing import Dict, Any
from .base_courier import BaseCourier
from .cancellable_courier_interface import CancellableCourierInterface
from ...schemas.shipment_request import ShipmentRequest
from ...schemas.shipment_response import ShipmentResponse
from ...schemas.label_response import LabelResponse
from ..http_clients.dhl_client import DHLHttpClient
from ..mapping.dhl.dhl_payload_builder import DHLPayloadBuilder
from ..mapping.dhl.dhl_response_mapper import DHLResponseMapper
from ..labels.dhl_label_response_parser import DHLLabelResponseParser
from ..tracking.dhl_tracking_response_parser import DHLTrackingResponseParser
from ..tracking.tracking_status_mapper import TrackingStatusMapper
from ...schemas.tracking_response import TrackingResponse

logger = logging.getLogger(__name__)


class DHLCourier(BaseCourier, CancellableCourierInterface):
    def _create_http_client(self):
        return DHLHttpClient(
            base_url=self.config.get('base_url', ''),
            api_key=self.config.get('api_key'),
            api_secret=self.config.get('api_secret'),
            username=self.config.get('username'),
            password=self.config.get('password'),
            timeout=30
        )
    
    def _prepare_payload(self, request: ShipmentRequest) -> Dict[str, Any]:
        return DHLPayloadBuilder.build_dhl_payload(request)
    
    def _map_response(self, response_data: Dict[str, Any]) -> ShipmentResponse:
        return DHLResponseMapper.map_dhl_response_to_shipment_response(
            response_data.get('data', {}),
            response_data.get('success', False)
        )
    
    def fetch_label(self, courier_external_id: str) -> LabelResponse:
        try:
            logger.info(f"DHL: Fetching label for shipment {courier_external_id}")
            
            response = self.http_client.get_label(courier_external_id)
            
            if response.get('success') and response.get('data'):
                label_data = DHLLabelResponseParser.parse_success_response(response['data'])
                if label_data:
                    return LabelResponse.from_dict(label_data)
                else:
                    return LabelResponse.create_error_response(
                        'Label URL not found in DHL response',
                        'LABEL_URL_NOT_FOUND'
                    )
            else:
                error_info = DHLLabelResponseParser.parse_error_response(
                    response.get('error', 'Failed to fetch label from DHL')
                )
                return LabelResponse.create_error_response(
                    error_info['error_message'],
                    error_info['error_code']
                )
                
        except Exception as e:
            logger.error(f"DHL: Error fetching label: {str(e)}")
            return LabelResponse.create_error_response(
                f'DHL API error: {str(e)}',
                'COURIER_API_ERROR'
            )
    
    def create_shipment(self, request: ShipmentRequest, shipment_type_id: int = None) -> ShipmentResponse:
        try:
            logger.info(f"DHL: Starting shipment creation")
            logger.info(f"DHL: Request details - Reference: {request.reference_number}, Weight: {request.weight.value} {request.weight.unit}, Dimensions: {request.dimensions.height}x{request.dimensions.width}x{request.dimensions.length} {request.dimensions.unit}, Shipper: {request.shipper.city}, Consignee: {request.consignee.city}")
            
            payload = self._prepare_payload(request)
            logger.info(f"DHL: Prepared payload")
            logger.debug(f"DHL: Full payload: {payload}")
            
            response_data = self.http_client.create_shipment(payload)
            
            shipment_response = self._map_response(response_data)
            
            logger.info(f"DHL: Shipment creation completed - Success: {shipment_response.success}")
            return shipment_response
            
        except Exception as e:
            logger.error(f"DHL: Error creating shipment: {str(e)}")
            return ShipmentResponse(
                success=False,
                error_message=f"DHL error: {str(e)}"
            )
    
    def track_shipment(self, courier_external_id: str) -> TrackingResponse:
        try:
            logger.info(f"DHL: Tracking shipment {courier_external_id}")
            
            response = self.http_client.track_shipment(courier_external_id)
            
            if response.get('success') and response.get('data'):
                tracking_data = DHLTrackingResponseParser.parse_tracking_response(response['data'])
                if tracking_data:
                    mapped_status = TrackingStatusMapper.map_courier_status('dhl', tracking_data['current_status'])
                    tracking_data['current_status'] = mapped_status['status']
                    tracking_data['status_description'] = mapped_status['description']
                    
                    mapped_events = []
                    for event in tracking_data.get('events', []):
                        mapped_event_status = TrackingStatusMapper.map_courier_status('dhl', event['status'])
                        event['status'] = mapped_event_status['status']
                        event['description'] = mapped_event_status['description']
                        mapped_events.append(event)
                    tracking_data['events'] = mapped_events
                    
                    return TrackingResponse.from_dict(tracking_data)
                else:
                    return TrackingResponse.create_error_response(
                        'Tracking data not found in DHL response',
                        'TRACKING_DATA_NOT_FOUND'
                    )
            else:
                error_info = DHLTrackingResponseParser.parse_error_response(
                    response.get('error', 'Failed to track shipment with DHL')
                )
                return TrackingResponse.create_error_response(
                    error_info['error_message'],
                    error_info['error_code']
                )
                
        except Exception as e:
            logger.error(f"DHL: Error tracking shipment: {str(e)}")
            return TrackingResponse.create_error_response(
                f'DHL API error: {str(e)}',
                'COURIER_API_ERROR'
            )
    
    def cancel_shipment(self, courier_external_id: str) -> Dict[str, Any]:
        try:
            logger.info(f"DHL: Cancelling shipment {courier_external_id}")
            
            cancel_response = self.http_client.cancel_shipment(courier_external_id)
            
            if cancel_response.get('success'):
                logger.info(f"DHL: Successfully cancelled shipment {courier_external_id}")
                return {
                    'success': True,
                    'message': 'Shipment cancelled successfully with DHL'
                }
            else:
                logger.warning(f"DHL: Failed to cancel shipment {courier_external_id}: {cancel_response.get('error')}")
                return {
                    'success': False,
                    'message': f"DHL cancellation failed: {cancel_response.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"DHL: Error cancelling shipment {courier_external_id}: {str(e)}")
            return {
                'success': False,
                'message': f'DHL cancellation error: {str(e)}'
            }