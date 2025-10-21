import logging
from typing import Dict, Any
from ....schemas.shipment_response import ShipmentResponse

logger = logging.getLogger(__name__)


class DHLResponseMapper:
    @classmethod
    def map_dhl_response_to_shipment_response(
        cls, 
        dhl_response: Dict[str, Any], 
        success: bool = True
    ) -> ShipmentResponse:
        try:
            if not success:
                if isinstance(dhl_response, str):
                    return ShipmentResponse(
                        success=False,
                        error_message=dhl_response,
                        raw_response={'error': dhl_response}
                    )
                else:
                    return ShipmentResponse(
                        success=False,
                        error_message=dhl_response.get('error_message', 'Unknown error'),
                        raw_response=dhl_response
                    )
            
            items = dhl_response.get('items', [])
            if not items:
                return ShipmentResponse(
                    success=False,
                    error_message="No shipment data in DHL response",
                    raw_response=dhl_response
                )
            
            item = items[0]
            tracking_number = item.get('shipmentNo', '')
            courier_reference = item.get('shipmentRefNo', '')
            
            from .dhl_status_mapper import DHLStatusMapper
            sstatus = item.get('sstatus', {})
            dhl_status = sstatus.get('status', 'UNKNOWN')
            mapped_status = DHLStatusMapper.map_dhl_status(str(dhl_status))
            
            return ShipmentResponse(
                success=True,
                tracking_number=tracking_number,
                courier_reference=courier_reference,
                estimated_delivery=None,  # DHL doesn't provide this in creation response
                cost=None,  # DHL doesn't provide this in creation response
                raw_response=dhl_response
            )
            
        except Exception as e:
            logger.error(f"DHLResponseMapper: Error mapping DHL response: {str(e)}")
            return ShipmentResponse(
                success=False,
                error_message=f"Error processing DHL response: {str(e)}",
                raw_response=dhl_response
            )
    
    @classmethod
    def extract_tracking_number(cls, dhl_response: Dict[str, Any]) -> str:
        """Extract tracking number from DHL response."""
        try:
            items = dhl_response.get('items', [])
            if items:
                return items[0].get('shipmentNo', '')
            return ''
        except Exception:
            return ''
    
    @classmethod
    def extract_courier_reference(cls, dhl_response: Dict[str, Any]) -> str:
        """Extract courier reference from DHL response."""
        try:
            items = dhl_response.get('items', [])
            if items:
                return items[0].get('shipmentRefNo', '')
            return ''
        except Exception:
            return ''
