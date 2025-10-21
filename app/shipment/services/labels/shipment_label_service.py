import logging
from typing import Dict, Any
from .label_cache_service import LabelCacheService
from ..shipments.shipment_lookup_service import ShipmentLookupService
from ...schemas.label_response import LabelResponse

logger = logging.getLogger(__name__)


class ShipmentLabelService:
    def __init__(self, 
                 courier_factory_instance=None,
                 cache_service: LabelCacheService = None,
                 lookup_service: ShipmentLookupService = None):
        self._courier_factory = courier_factory_instance
        self._cache_service = cache_service or LabelCacheService()
        self._lookup_service = lookup_service or ShipmentLookupService()
    
    def get_shipment_label_by_reference(self, reference_number: str) -> LabelResponse:
        try:
            logger.info(f"ShipmentLabelService: Getting label for reference {reference_number}")
            
            cached_label = self._cache_service.get_cached_label(reference_number)
            if cached_label:
                logger.info(f"ShipmentLabelService: Found cached label for reference {reference_number}")
                return cached_label
            
            shipment = self._lookup_service.get_shipment_by_reference(reference_number)
            if not shipment:
                return LabelResponse.create_error_response(
                    'Shipment not found',
                    'SHIPMENT_NOT_FOUND'
                )
            
            if not self._courier_factory:
                from ..couriers.courier_factory import courier_factory
                self._courier_factory = courier_factory
            
            courier_name = shipment.courier.name.lower()
            label_data = self._courier_factory.fetch_label(courier_name, shipment.courier_external_id)
            if not label_data['success']:
                return LabelResponse.create_error_response(
                    label_data['error'],
                    label_data['error_code']
                )
            
            saved_label = self._cache_service.save_label(
                shipment_id=shipment.id,
                reference_number=reference_number,
                url=label_data['url'],
                format=label_data['format']
            )
            
            if not saved_label:
                return LabelResponse.create_error_response(
                    'Failed to save label to database',
                    'DATABASE_ERROR'
                )
            
            logger.info(f"ShipmentLabelService: Successfully retrieved and saved label for reference {reference_number}")
            return saved_label
            
        except Exception as e:
            logger.error(f"ShipmentLabelService: Error getting label for reference {reference_number}: {str(e)}")
            return LabelResponse.create_error_response(
                f'Internal server error: {str(e)}',
                'INTERNAL_ERROR'
            )
