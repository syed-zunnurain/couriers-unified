import logging
from typing import Dict, Any
from ..courier_interface import CourierInterface, CourierRequest, CourierResponse

logger = logging.getLogger(__name__)


class DHLCourier(CourierInterface):
    """DHL courier implementation."""
    
    def create_shipment(self, request: CourierRequest) -> CourierResponse:
        """Create shipment with DHL (dummy response for testing)."""
        logger.info(f"DHLCourier: Starting shipment creation - origin='{request.origin}', destination='{request.destination}', weight={request.weight}")
        
        # Return dummy response for testing
        import random
        from datetime import datetime, timedelta
        
        # Simulate 90% success rate
        success_chance = random.random()
        logger.info(f"DHLCourier: Random success chance = {success_chance:.3f} (need < 0.9 for success)")
        
        if success_chance < 0.9:
            logger.info("DHLCourier: Generating successful dummy response")
            # Generate dummy tracking number
            tracking_number = f"DHL{random.randint(100000000, 999999999)}"
            
            # Generate dummy courier reference
            courier_reference = f"DHL-REF-{random.randint(10000, 99999)}"
            
            # Generate estimated delivery (1-3 days from now)
            estimated_delivery = (datetime.now() + timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d")
            
            # Generate dummy cost
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
            # Simulate 10% failure rate
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
            "shipmentType": request.shipment_type,
            "origin": {
                "city": request.origin
            },
            "destination": {
                "city": request.destination
            },
            "weight": request.weight,
            "dimensions": request.dimensions,
            "items": request.items,
            "pickupDate": request.pickup_date,
            "specialInstructions": request.special_instructions,
            "referenceNumber": request.reference_number
        }
