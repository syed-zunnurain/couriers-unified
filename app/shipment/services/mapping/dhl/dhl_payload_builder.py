import logging
from typing import Dict, Any
from ....schemas.shipment_request import ShipmentRequest

logger = logging.getLogger(__name__)


class DHLPayloadBuilder:
    @classmethod
    def build_dhl_payload(cls, request: ShipmentRequest) -> Dict[str, Any]:
        from .dhl_product_mapper import DHLProductMapper
        
        return {
            "shipments": [{
                "product": DHLProductMapper.map_shipment_type_to_dhl_product(request.shipment_type),
                "refNo": request.reference_number,
                "billingNumber": "33333333330102",
                "shipper": {
                    "name1": request.shipper.name,
                    "addressStreet": request.shipper.address,
                    "city": request.shipper.city,
                    "country": request.shipper.country,
                    "phone": request.shipper.phone,
                    "email": request.shipper.email,
                    "postalCode": request.shipper.postal_code or ""
                },
                "consignee": {
                    "name1": request.consignee.name,
                    "addressStreet": request.consignee.address,
                    "city": request.consignee.city,
                    "country": request.consignee.country,
                    "phone": request.consignee.phone,
                    "email": request.consignee.email,
                    "postalCode": request.consignee.postal_code or ""
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
    
    @classmethod
    def build_dhl_tracking_payload(cls, tracking_number: str) -> Dict[str, Any]:
        """Build DHL tracking payload (for future use)."""
        return {
            "trackingNumber": tracking_number
        }
    
    @classmethod
    def validate_dhl_payload(cls, payload: Dict[str, Any]) -> bool:
        """Validate DHL payload structure."""
        try:
            shipments = payload.get('shipments', [])
            if not shipments:
                return False
            
            shipment = shipments[0]
            required_fields = ['product', 'refNo', 'shipper', 'consignee', 'details']
            return all(field in shipment for field in required_fields)
        except Exception:
            return False
