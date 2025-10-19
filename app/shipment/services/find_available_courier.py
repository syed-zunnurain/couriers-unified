import logging
from ..repositories.repository_factory import repositories

logger = logging.getLogger(__name__)


class FindAvailableCourier:
    """Class for finding available courier for the given shipment type and route."""
    
    def find(self, shipment_type_id, shipper_city, consignee_city):
        """Find an available courier for the given shipment type and route."""
        try:
            # Get available couriers for the shipment type
            courier_shipment_types = repositories.courier_shipment_type.get_by_shipment_type(shipment_type_id)
            
            # Get available couriers for the route
            courier_routes = repositories.courier_route.get_by_route(shipper_city, consignee_city)
            
            # Find intersection of couriers that support both shipment type and route
            available_courier_ids = set()
            for cst in courier_shipment_types:
                for cr in courier_routes:
                    if cst.courier_id == cr.courier_id:
                        available_courier_ids.add(cst.courier_id)
            
            if available_courier_ids:
                return repositories.courier.get_by_id(list(available_courier_ids)[0])
            else:
                return None
                
        except Exception as e:
            logger.error(f'Error finding available courier: {str(e)}')
            return None
    

