"""Service for shipment lookup operations."""

import logging
from shipment.repositories.repository_factory import repositories

logger = logging.getLogger(__name__)


class ShipmentLookupService:
    """Service for shipment lookup operations."""
    
    def __init__(self):
        self._shipment_repo = repositories.shipment
    
    def get_shipment_by_reference(self, reference_number: str):
        """
        Get shipment by reference number.
        
        Args:
            reference_number: The shipment reference number
            
        Returns:
            Shipment object or None
        """
        try:
            logger.info(f"ShipmentLookupService: Looking up shipment for reference {reference_number}")
            shipment = self._shipment_repo.get_by_reference_number(reference_number)
            if shipment:
                logger.info(f"ShipmentLookupService: Found shipment {shipment.id} for reference {reference_number}")
            else:
                logger.info(f"ShipmentLookupService: No shipment found for reference {reference_number}")
            return shipment
        except Exception as e:
            logger.error(f"ShipmentLookupService: Error getting shipment: {str(e)}")
            return None
