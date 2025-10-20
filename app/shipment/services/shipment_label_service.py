"""Simple service for orchestrating shipment label operations."""

import logging
from typing import Dict, Any
from .courier_factory import courier_factory
from .label_cache_service import LabelCacheService
from .shipment_lookup_service import ShipmentLookupService

logger = logging.getLogger(__name__)


class ShipmentLabelService:
    """Simple service for orchestrating shipment label operations."""
    
    def __init__(self, 
                 courier_factory_instance=None,
                 cache_service: LabelCacheService = None,
                 lookup_service: ShipmentLookupService = None):
        self._courier_factory = courier_factory_instance or courier_factory
        self._cache_service = cache_service or LabelCacheService()
        self._lookup_service = lookup_service or ShipmentLookupService()
    
    def get_shipment_label_by_reference(self, reference_number: str) -> Dict[str, Any]:
        """
        Get shipment label by reference number.
        
        Args:
            reference_number: The shipment reference number
            
        Returns:
            Dict containing label information or error
        """
        try:
            logger.info(f"ShipmentLabelService: Getting label for reference {reference_number}")
            
            # 1. Try to get from cache first
            cached_label = self._cache_service.get_cached_label(reference_number)
            if cached_label:
                logger.info(f"ShipmentLabelService: Found cached label for reference {reference_number}")
                return {
                    'success': True,
                    'label': cached_label
                }
            
            # 2. If not found, get shipment and fetch from courier
            shipment = self._lookup_service.get_shipment_by_reference(reference_number)
            if not shipment:
                return {
                    'success': False,
                    'error': 'Shipment not found',
                    'error_code': 'SHIPMENT_NOT_FOUND'
                }
            
            # 3. Fetch from courier using factory
            courier_name = shipment.courier.name.lower()
            label_data = self._courier_factory.fetch_label(courier_name, shipment.courier_external_id)
            if not label_data['success']:
                return label_data
            
            # 4. Save to cache
            saved_label = self._cache_service.save_label(
                shipment_id=shipment.id,
                reference_number=reference_number,
                url=label_data['url'],
                format=label_data['format']
            )
            
            if not saved_label:
                return {
                    'success': False,
                    'error': 'Failed to save label to database',
                    'error_code': 'DATABASE_ERROR'
                }
            
            logger.info(f"ShipmentLabelService: Successfully retrieved and saved label for reference {reference_number}")
            return {
                'success': True,
                'label': saved_label
            }
            
        except Exception as e:
            logger.error(f"ShipmentLabelService: Error getting label for reference {reference_number}: {str(e)}")
            return {
                'success': False,
                'error': f'Internal server error: {str(e)}',
                'error_code': 'INTERNAL_ERROR'
            }
