"""Service for label caching operations."""

import logging
from typing import Dict, Any, Optional
from ...repositories.repository_factory import repositories
from ...schemas.label_response import LabelResponse

logger = logging.getLogger(__name__)


class LabelCacheService:
    """Service for label caching operations."""
    
    def __init__(self):
        self._shipment_label_repo = repositories.shipment_label
    
    def get_cached_label(self, reference_number: str) -> Optional[LabelResponse]:
        """
        Get active label by reference number.
        
        Args:
            reference_number: The shipment reference number
            
        Returns:
            LabelResponse if found and active, None otherwise
        """
        try:
            existing_label = self._shipment_label_repo.get_active_by_reference_number(reference_number)
            if existing_label:
                logger.info(f"LabelCacheService: Found active label for reference {reference_number}")
                return LabelResponse.create_success_response(
                    id=existing_label.id,
                    reference_number=existing_label.reference_number,
                    url=existing_label.url,
                    format=existing_label.format,
                    is_active=existing_label.is_active,
                    created_at=existing_label.created_at.isoformat()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"LabelCacheService: Error getting cached label: {str(e)}")
            return None
    
    def save_label(self, shipment_id: int, reference_number: str, 
                   url: str, format: str) -> Optional[LabelResponse]:
        """
        Save label to cache.
        
        Args:
            shipment_id: The shipment ID
            reference_number: The reference number
            url: The label URL
            format: The label format
            
        Returns:
            LabelResponse with saved label data or None
        """
        try:
            # Deactivate any existing labels for this shipment
            self._shipment_label_repo.deactivate_labels_by_shipment(shipment_id)
            
            # Create new active label
            label = self._shipment_label_repo.create_label(
                shipment_id=shipment_id,
                reference_number=reference_number,
                url=url,
                format=format,
                is_active=True
            )
            
            logger.info(f"LabelCacheService: Saved label {label.id} for shipment {shipment_id}")
            return LabelResponse.create_success_response(
                id=label.id,
                reference_number=label.reference_number,
                url=label.url,
                format=label.format,
                is_active=label.is_active,
                created_at=label.created_at.isoformat()
            )
            
        except Exception as e:
            logger.error(f"LabelCacheService: Error saving label: {str(e)}")
            return None
