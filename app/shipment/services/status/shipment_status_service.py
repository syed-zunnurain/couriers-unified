import logging
from typing import Optional, List
from django.db import transaction
from ...models import Shipment, ShipmentStatus
from ..mapping.status_mapping_service import StatusMappingService

logger = logging.getLogger(__name__)

class ShipmentStatusService:
    @classmethod
    def create_status(cls, 
                     shipment: Shipment, 
                     status: str, 
                     address: Optional[str] = None,
                     postal_code: Optional[str] = None,
                     country: Optional[str] = None) -> ShipmentStatus:
        if not StatusMappingService.is_valid_status(status):
            logger.warning(f"ShipmentStatusService: Invalid status '{status}' for shipment {shipment.reference_number}")
            status = 'unknown'
        
        with transaction.atomic():
            status_entry = ShipmentStatus.objects.create(
                shipment=shipment,
                status=status.lower(),
                address=address,
                postal_code=postal_code,
                country=country
            )
            
            logger.info(f"ShipmentStatusService: Created status '{status}' for shipment {shipment.reference_number}")
            return status_entry
    
    @classmethod
    def get_latest_status(cls, shipment: Shipment) -> Optional[ShipmentStatus]:
        return ShipmentStatus.objects.filter(shipment=shipment).order_by('-created_at').first()
    
    @classmethod
    def get_status_history(cls, shipment: Shipment) -> List[ShipmentStatus]:
        return list(ShipmentStatus.objects.filter(shipment=shipment).order_by('created_at'))
    
    @classmethod
    def update_status_from_courier(cls, 
                                  shipment: Shipment, 
                                  courier_name: str, 
                                  courier_status: str,
                                  address: Optional[str] = None,
                                  postal_code: Optional[str] = None,
                                  country: Optional[str] = None) -> ShipmentStatus:
        """Update status from courier-specific status."""
        
        # Map courier status to standardized status
        standardized_status = StatusMappingService.map_courier_status(courier_name, courier_status)
        
        return cls.create_status(
            shipment=shipment,
            status=standardized_status,
            address=address,
            postal_code=postal_code,
            country=country
        )
    
    @classmethod
    def get_status_summary(cls, shipment: Shipment) -> dict:
        """Get status summary for a shipment."""
        latest_status = cls.get_latest_status(shipment)
        status_history = cls.get_status_history(shipment)
        
        return {
            'shipment_id': shipment.id,
            'reference_number': shipment.reference_number,
            'current_status': latest_status.status if latest_status else 'unknown',
            'status_display': StatusMappingService.get_status_display_name(latest_status.status) if latest_status else 'Unknown',
            'total_updates': len(status_history),
            'last_updated': latest_status.created_at if latest_status else None,
            'status_history': [
                {
                    'status': status.status,
                    'status_display': StatusMappingService.get_status_display_name(status.status),
                    'address': status.address,
                    'postal_code': status.postal_code,
                    'country': status.country,
                    'created_at': status.created_at
                }
                for status in status_history
            ]
        }
