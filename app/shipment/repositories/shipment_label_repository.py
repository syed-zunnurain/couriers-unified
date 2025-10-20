from typing import List, Optional
from django.db import transaction
from ..models import ShipmentLabel
from .base_repository import DjangoRepository


class ShipmentLabelRepository(DjangoRepository):
    """Repository for ShipmentLabel model operations."""
    
    def __init__(self):
        super().__init__(ShipmentLabel)
    
    def get_by_shipment_id(self, shipment_id: int) -> List[ShipmentLabel]:
        """Get all labels for a specific shipment."""
        return self.filter(shipment_id=shipment_id)
    
    def get_active_by_shipment_id(self, shipment_id: int) -> List[ShipmentLabel]:
        """Get active labels for a specific shipment."""
        return self.filter(shipment_id=shipment_id, is_active=True)
    
    def get_by_reference_number(self, reference_number: str) -> Optional[ShipmentLabel]:
        """Get label by reference number."""
        return self.first(reference_number=reference_number)
    
    def get_active_by_reference_number(self, reference_number: str) -> Optional[ShipmentLabel]:
        """Get active label by reference number."""
        return self.first(reference_number=reference_number, is_active=True)
    
    def get_by_format(self, format: str) -> List[ShipmentLabel]:
        """Get labels by format."""
        return self.filter(format=format)
    
    def get_active_labels(self) -> List[ShipmentLabel]:
        """Get all active labels."""
        return self.filter(is_active=True)
    
    def get_inactive_labels(self) -> List[ShipmentLabel]:
        """Get all inactive labels."""
        return self.filter(is_active=False)
    
    def create_label(
        self,
        shipment_id: int,
        reference_number: str,
        url: str,
        format: str,
        is_active: bool = True
    ) -> ShipmentLabel:
        """Create a new shipment label."""
        return self.create(
            shipment_id=shipment_id,
            reference_number=reference_number,
            url=url,
            format=format,
            is_active=is_active
        )
    
    def deactivate_label(self, label_id: int) -> Optional[ShipmentLabel]:
        """Deactivate a label by setting is_active to False."""
        return self.update(label_id, is_active=False)
    
    def activate_label(self, label_id: int) -> Optional[ShipmentLabel]:
        """Activate a label by setting is_active to True."""
        return self.update(label_id, is_active=True)
    
    def deactivate_labels_by_shipment(self, shipment_id: int) -> int:
        """Deactivate all labels for a specific shipment."""
        return self.model.objects.filter(shipment_id=shipment_id).update(is_active=False)
    
    def get_latest_by_shipment_id(self, shipment_id: int) -> Optional[ShipmentLabel]:
        """Get the latest label for a specific shipment."""
        try:
            return self.model.objects.filter(
                shipment_id=shipment_id
            ).order_by('-created_at').first()
        except self.model.DoesNotExist:
            return None
    
    def get_latest_active_by_shipment_id(self, shipment_id: int) -> Optional[ShipmentLabel]:
        """Get the latest active label for a specific shipment."""
        try:
            return self.model.objects.filter(
                shipment_id=shipment_id,
                is_active=True
            ).order_by('-created_at').first()
        except self.model.DoesNotExist:
            return None
    
    def exists_by_shipment_and_reference(self, shipment_id: int, reference_number: str) -> bool:
        """Check if a label exists for a shipment with the given reference number."""
        return self.exists(shipment_id=shipment_id, reference_number=reference_number)
    
    def get_labels_by_date_range(self, start_date, end_date) -> List[ShipmentLabel]:
        """Get labels created within a date range."""
        return self.filter(created_at__date__range=[start_date, end_date])
    
    def get_labels_by_shipment_date_range(self, shipment_id: int, start_date, end_date) -> List[ShipmentLabel]:
        """Get labels for a specific shipment within a date range."""
        return self.filter(
            shipment_id=shipment_id,
            created_at__date__range=[start_date, end_date]
        )
    
    def update_label_url(self, label_id: int, url: str) -> Optional[ShipmentLabel]:
        """Update the URL of a label."""
        return self.update(label_id, url=url)
    
    def get_labels_by_format_and_shipment(self, format: str, shipment_id: int) -> List[ShipmentLabel]:
        """Get labels by format for a specific shipment."""
        return self.filter(format=format, shipment_id=shipment_id)
