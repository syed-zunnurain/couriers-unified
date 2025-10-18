import logging
import requests
from typing import Dict, Any
from ..courier_interface import CourierInterface, CourierRequest, CourierResponse
from ..shipment_persistence_service import ShipmentPersistenceService

logger = logging.getLogger(__name__)


class DHLCourier(CourierInterface):
    """DHL courier implementation."""
    
    def __init__(self, courier_name: str, config: Dict[str, Any], courier_obj=None):
        super().__init__(courier_name, config)
        self.courier_obj = courier_obj
    
    def create_shipment(self, request: CourierRequest, shipment_type_id: int = None) -> CourierResponse:
        """Create shipment with DHL API."""
        logger.info(f"DHLCourier: Starting shipment creation - origin='{request.route.origin}', destination='{request.route.destination}', weight={request.weight}")

        dhl_payload = self._prepare_dhl_payload(request)
        logger.info(f"DHLCourier: DHL payload = {dhl_payload}")
        
        try:
            # Make API call to DHL
            response = self._call_dhl_api(dhl_payload)
            
            if response.get('success'):
                logger.info("DHLCourier: Successfully created shipment with DHL API")
                
                # Create courier response
                courier_response = CourierResponse(
                    success=True,
                    tracking_number=response.get('tracking_number'),
                    courier_reference=response.get('courier_reference'),
                    estimated_delivery=response.get('estimated_delivery'),
                    cost=response.get('cost'),
                    raw_response=response.get('raw_response')
                )
                
                # Persist shipment data to database
                try:
                    if self.courier_obj and shipment_type_id:
                        shipment = ShipmentPersistenceService.create_shipment(
                            request, courier_response, self.courier_obj, shipment_type_id
                        )
                        logger.info(f"DHLCourier: Persisted shipment {shipment.id} to database")
                    else:
                        logger.warning("DHLCourier: No courier object or shipment_type_id available for persistence")
                except Exception as e:
                    logger.error(f"DHLCourier: Error persisting shipment to database: {str(e)}")
                    # Don't fail the entire request if persistence fails
                
                return courier_response
            else:
                logger.warning(f"DHLCourier: DHL API call failed: {response.get('error_message')}")
                return CourierResponse(
                    success=False,
                    error_message=response.get('error_message'),
                    raw_response=response.get('raw_response')
                )
                
        except Exception as e:
            logger.error(f"DHLCourier: Error calling DHL API: {str(e)}")
            return CourierResponse(
                success=False,
                error_message=f"DHL API error: {str(e)}",
                raw_response={"error": str(e)}
            )
        
    
    def _prepare_dhl_payload(self, request: CourierRequest) -> Dict[str, Any]:
        """Convert standardized request to DHL-specific format."""
        
        return {
            "shipments": [{
                "product": "V01PAK",
                "refNo": request.reference_number,
                "billingNumber": "33333333330102",
                "shipper": {
                    "name1": request.shipper.name,
                    "addressStreet": request.shipper.address,
                    "city": request.shipper.city,
                    "country": request.shipper.country,
                    "phone": request.shipper.phone,
                    "email": request.shipper.email,
                    "postalCode": request.shipper.postal_code
                },
                "consignee": {
                    "name1": request.consignee.name,
                    "addressStreet": request.consignee.address,
                    "city": request.consignee.city,
                    "country": request.consignee.country,
                    "phone": request.consignee.phone,
                    "email": request.consignee.email,
                    "postalCode": request.consignee.postal_code
                },
                "details": {
                    "dim": {
                        "uom": request.dimensions.unit,
                        "length": request.dimensions.length,
                        "width": request.dimensions.width,
                        "height": request.dimensions.height
                    },
                    "weight": {
                        "uom": request.weight.unit,
                        "value": request.weight.value
                    },
                }
            }]
        }
    
    def _call_dhl_api(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call to DHL parcel shipping endpoint."""
        try:
            # Construct the full URL
            base_url = self.config.get('base_url', '').rstrip('/')
            endpoint = "parcel/de/shipping/v2/orders"
            url = f"{base_url}/{endpoint}?validate=false"
            
            logger.info(f"DHLCourier: Making API call to {url}")

            token = "KzGjPhi60chchfJyVbmwQyeJcUZz"
            headers = {
                'Authorization': f"Bearer {token}"
            }
            
            # Make the API call
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"DHLCourier: API response status: {response.status_code}")
            logger.info(f"DHLCourier: API response body: {response.text}")
            
            # Parse response
            if response.status_code == 200:
                response_data = response.json()
                return {
                    'success': True,
                    'tracking_number': self._extract_tracking_number(response_data),
                    'courier_reference': self._extract_courier_reference(response_data),
                    'raw_response': response_data
                }
            else:
                error_message = f"DHL API error: HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', error_message)
                except:
                    error_message = f"{error_message} - {response.text}"
                
                return {
                    'success': False,
                    'error_message': error_message,
                    'raw_response': {
                        'status_code': response.status_code,
                        'response': response.text
                    }
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"DHLCourier: Request exception: {str(e)}")
            return {
                'success': False,
                'error_message': f"Network error: {str(e)}",
                'raw_response': {"error": str(e)}
            }
        except Exception as e:
            logger.error(f"DHLCourier: Unexpected error: {str(e)}")
            return {
                'success': False,
                'error_message': f"Unexpected error: {str(e)}",
                'raw_response': {"error": str(e)}
            }
    
    def _extract_tracking_number(self, response_data: Dict[str, Any]) -> str:
        """Extract tracking number from DHL API response."""
        # Extract from DHL API response structure
        items = response_data.get('items', [])
        if items and len(items) > 0:
            return items[0].get('shipmentNo', '')
        return ''
    
    def _extract_courier_reference(self, response_data: Dict[str, Any]) -> str:
        """Extract courier reference from DHL API response."""
        # Extract from DHL API response structure
        items = response_data.get('items', [])
        if items and len(items) > 0:
            return items[0].get('shipmentNo', '')
        return ''
