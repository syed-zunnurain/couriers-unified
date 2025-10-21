import logging
from collections import defaultdict
from datetime import datetime, timedelta
from ...repositories.repository_factory import repositories

logger = logging.getLogger(__name__)


class FindAvailableCourier:
    def find(self, shipment_type_id, shipper_city, consignee_city):
        try:
            courier_shipment_types = repositories.courier_shipment_type.get_by_shipment_type(shipment_type_id)
            
            courier_routes = repositories.courier_route.get_by_route(shipper_city, consignee_city)
            
            available_courier_ids = set()
            for cst in courier_shipment_types:
                for cr in courier_routes:
                    if cst.courier_id == cr.courier_id:
                        available_courier_ids.add(cst.courier_id)
            
            if available_courier_ids:
                available_couriers = []
                for courier_id in available_courier_ids:
                    courier = repositories.courier.get_by_id(courier_id)
                    if courier and courier.is_active:
                        available_couriers.append(courier)
                
                if available_couriers:
                    selected_courier = self._round_robin_selection(available_couriers, shipment_type_id, shipper_city, consignee_city)
                    logger.info(f'Selected courier: {selected_courier.name} using round-robin')
                    return selected_courier
                else:
                    logger.warning('No active couriers found')
                    return None
            else:
                logger.warning(f'No available couriers found for shipment_type_id={shipment_type_id}, route={shipper_city}->{consignee_city}')
                return None
                
        except Exception as e:
            logger.error(f'Error finding available courier: {str(e)}')
            return None
    
    def _round_robin_selection(self, available_couriers, shipment_type_id, shipper_city, consignee_city):
        try:
            if len(available_couriers) == 1:
                logger.info(f'Only one courier available: {available_couriers[0].name}')
                return available_couriers[0]
            
            cutoff_date = datetime.now() - timedelta(days=7)
            recent_shipments = repositories.shipment.filter(
                shipment_type_id=shipment_type_id,
                created_at__gte=cutoff_date
            )
            
            route_shipments = []
            for shipment in recent_shipments:
                if (shipment.shipper.city.lower() == shipper_city.lower() and 
                    shipment.consignee.city.lower() == consignee_city.lower()):
                    route_shipments.append(shipment)
            
            courier_usage = defaultdict(int)
            for shipment in route_shipments:
                courier_usage[shipment.courier_id] += 1
            
            sorted_couriers = sorted(available_couriers, key=lambda c: (courier_usage[c.id], c.name))
            
            return sorted_couriers[0] if sorted_couriers else None
            
        except Exception as e:
            logger.error(f'Error in round-robin selection: {str(e)}')
            return available_couriers[0] if available_couriers else None

