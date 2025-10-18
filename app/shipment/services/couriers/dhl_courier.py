import logging
from typing import Dict, Any
from ..courier_interface import CourierInterface, CourierRequest, CourierResponse

logger = logging.getLogger(__name__)


class DHLCourier(CourierInterface):
    """DHL courier implementation."""
    
    def create_shipment(self, request: CourierRequest) -> CourierResponse:
        """Create shipment with DHL (dummy response for testing)."""
        logger.info(f"DHLCourier: Starting shipment creation - origin='{request.route.origin}', destination='{request.route.destination}', weight={request.weight}")

        dhl_payload = self._prepare_dhl_payload(request)
        logger.info(f"DHLCourier: DHL payload = {dhl_payload}")
        
        import random
        from datetime import datetime, timedelta
        success_chance = random.random()
        logger.info(f"DHLCourier: Random success chance = {success_chance:.3f} (need < 0.9 for success)")
        
        if success_chance < 0.9:
            logger.info("DHLCourier: Generating successful dummy response")
            tracking_number = f"DHL{random.randint(100000000, 999999999)}"
            courier_reference = f"DHL-REF-{random.randint(10000, 99999)}"
            estimated_delivery = (datetime.now() + timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d")
            cost = round(random.uniform(15.0, 50.0), 2)
            
            logger.info(f"DHLCourier: Generated dummy data - tracking={tracking_number}, reference={courier_reference}, delivery={estimated_delivery}, cost=${cost}")
            
            return CourierResponse(
                success=True,
                tracking_number=tracking_number,
                courier_reference=courier_reference,
                estimated_delivery=estimated_delivery,
                cost=cost,
                raw_response={
                    "status": "success",
                    "message": "Dummy DHL shipment created successfully",
                    "trackingNumber": tracking_number,
                    "shipmentId": courier_reference,
                    "estimatedDelivery": estimated_delivery,
                    "cost": cost
                }
            )
        else:
            logger.warning("DHLCourier: Generating failure dummy response (10% chance)")
            return CourierResponse(
                success=False,
                error_message="Dummy DHL API error: Service temporarily unavailable",
                raw_response={
                    "status": "error",
                    "message": "Dummy DHL API error: Service temporarily unavailable"
                }
            )
    
    def _prepare_dhl_payload(self, request: CourierRequest) -> Dict[str, Any]:
        """Convert standardized request to DHL-specific format."""
        return {
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
        }
