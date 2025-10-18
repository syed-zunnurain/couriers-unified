import logging
from core.models import Courier, CourierShipmentType, CourierRoute

logger = logging.getLogger(__name__)


class FindAvailableCourier:
    """Class for finding available courier for the given shipment type and route."""
    
    def find(self, shipment_type_id, shipper_city, consignee_city):
        """Find an available courier for the given shipment type and route."""
        try:
            courier_shipment_types = CourierShipmentType.objects.filter(
                shipment_type_id=shipment_type_id,
                courier__is_active=True
            )
            
            courier_routes = CourierRoute.objects.filter(
                route__origin__iexact=shipper_city,
                route__destination__iexact=consignee_city,
                is_active=True,
                courier__is_active=True
            )
            
            available_courier_ids = set()
            for cst in courier_shipment_types:
                for cr in courier_routes:
                    if cst.courier_id == cr.courier_id:
                        available_courier_ids.add(cst.courier_id)
            
            if available_courier_ids:
                return Courier.objects.filter(id__in=available_courier_ids).first()
            else:
                return None
                
        except Exception as e:
            logger.error(f'Error finding available courier: {str(e)}')
            return None
    

