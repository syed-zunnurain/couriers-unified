from typing import List, Optional
from django.db import transaction
from ..models import Shipment
from .base_repository import DjangoRepository


class ShipmentRepository(DjangoRepository):
    """Repository for Shipment model operations."""
    
    def __init__(self):
        super().__init__(Shipment)
    
    def get_by_reference_number(self, reference_number: str) -> Optional[Shipment]:
        """Get shipment by reference number."""
        return self.first(reference_number=reference_number)
    
    def get_latest_by_reference_number(self, reference_number: str) -> Optional[Shipment]:
        """Get the latest shipment by reference number ordered by updated_at."""
        try:
            return self.model.objects.filter(
                reference_number=reference_number
            ).order_by('-updated_at').first()
        except self.model.DoesNotExist:
            return None
    
    def get_by_courier_external_id(self, courier_external_id: str) -> Optional[Shipment]:
        """Get shipment by courier external ID."""
        return self.first(courier_external_id=courier_external_id)
    
    def get_by_courier(self, courier_id: int) -> List[Shipment]:
        """Get all shipments for a specific courier."""
        return self.filter(courier_id=courier_id)
    
    def get_by_status(self, status: str) -> List[Shipment]:
        """Get shipments by status (if status field exists)."""
        if hasattr(self.model, 'status'):
            return self.filter(status=status)
        return []
    
    def get_recent_shipments(self, limit: int = 10) -> List[Shipment]:
        """Get recent shipments ordered by created_at."""
        return list(self.model.objects.order_by('-created_at')[:limit])
    
    def create_shipment(
        self,
        courier_id: int,
        shipment_type_id: int,
        courier_external_id: str,
        reference_number: str,
        shipper_id: int,
        route_id: int,
        consignee_id: int,
        height: int,
        width: int,
        length: int,
        dimension_unit: str,
        weight: float,
        weight_unit: str
    ) -> Shipment:
        """Create a new shipment with all required fields."""
        return self.create(
            courier_id=courier_id,
            shipment_type_id=shipment_type_id,
            courier_external_id=courier_external_id,
            reference_number=reference_number,
            shipper_id=shipper_id,
            route_id=route_id,
            consignee_id=consignee_id,
            height=height,
            width=width,
            length=length,
            dimension_unit=dimension_unit,
            weight=weight,
            weight_unit=weight_unit
        )
    
    def update_tracking_info(
        self,
        shipment_id: int,
        courier_external_id: str = None,
        tracking_number: str = None,
        estimated_delivery: str = None,
        cost: float = None
    ) -> Optional[Shipment]:
        """Update shipment with tracking information."""
        update_data = {}
        
        if courier_external_id is not None:
            update_data['courier_external_id'] = courier_external_id
        
        if tracking_number is not None and hasattr(self.model, 'tracking_number'):
            update_data['tracking_number'] = tracking_number
        
        if estimated_delivery is not None and hasattr(self.model, 'estimated_delivery'):
            update_data['estimated_delivery'] = estimated_delivery
        
        if cost is not None and hasattr(self.model, 'cost'):
            update_data['cost'] = cost
        
        return self.update(shipment_id, **update_data)
    
    def exists_by_reference_number(self, reference_number: str) -> bool:
        """Check if a shipment exists with the given reference number."""
        return self.exists(reference_number=reference_number)
    
    def get_shipments_by_date_range(self, start_date, end_date) -> List[Shipment]:
        """Get shipments created within a date range."""
        return self.filter(created_at__date__range=[start_date, end_date])
    
    def get_shipments_by_weight_range(self, min_weight: float, max_weight: float) -> List[Shipment]:
        """Get shipments within a weight range."""
        return self.filter(weight__range=[min_weight, max_weight])
