"""Service for converting request data to courier format."""

import logging
from typing import Dict, Any
from ..couriers.courier_interface import CourierRequest, Weight, Dimensions
from ...repositories.repository_factory import repositories

logger = logging.getLogger(__name__)


class RequestDataConverter:
    """Handles conversion of request data to courier format following SRP."""
    
    def convert_to_courier_request(self, request_data: Dict[str, Any], reference_number: str, shipper, consignee) -> CourierRequest:
        """Convert request data to CourierRequest format."""
        logger.info(f"RequestDataConverter: Converting request data to CourierRequest format")
        
        route, created = repositories.route.get_or_create_by_cities(
            shipper.city,
            consignee.city
        )
        
        weight = Weight(
            value=request_data.get('weight', 0.0),
            unit=request_data.get('weight_unit', 'kg')
        )
        
        dimensions_data = request_data.get('dimensions', {})
        dimensions = Dimensions(
            height=dimensions_data.get('height', 0.0),
            width=dimensions_data.get('width', 0.0),
            length=dimensions_data.get('length', 0.0),
            unit=request_data.get('dimension_unit', 'cm')
        )
        
        return CourierRequest(
            shipment_type=request_data.get('shipment_type', 'standard'),
            reference_number=reference_number,
            shipper=shipper,
            consignee=consignee,
            route=route,
            weight=weight,
            dimensions=dimensions,
            pickup_date=request_data.get('pickup_date'),
            special_instructions=request_data.get('special_instructions')
        )
