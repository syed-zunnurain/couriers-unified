"""Service for orchestrating shipment tracking operations."""

import logging
from typing import Dict, Any
from ..shipments.shipment_lookup_service import ShipmentLookupService
from ...schemas.tracking_response import TrackingResponse

logger = logging.getLogger(__name__)


class ShipmentTrackingService:
    """Service for orchestrating shipment tracking operations."""
    
    def __init__(self, 
                 courier_factory_instance=None,
                 lookup_service: ShipmentLookupService = None):
        self._courier_factory = courier_factory_instance
        self._lookup_service = lookup_service or ShipmentLookupService()
    
    def track_shipment_by_reference(self, reference_number: str) -> TrackingResponse:
        """
        Track shipment by reference number.
        
        Args:
            reference_number: The shipment reference number
            
        Returns:
            TrackingResponse containing tracking information or error
        """
        try:
            logger.info(f"ShipmentTrackingService: Tracking shipment for reference {reference_number}")
            
            shipment = self._lookup_service.get_shipment_by_reference(reference_number)
            if not shipment:
                return TrackingResponse.create_error_response(
                    'Shipment not found',
                    'SHIPMENT_NOT_FOUND'
                )
            
            if not self._courier_factory:
                from ..couriers.courier_factory import courier_factory
                self._courier_factory = courier_factory
            
            courier_name = shipment.courier.name.lower()
            tracking_response = self._courier_factory.track_shipment(courier_name, shipment.courier_external_id)
            if not tracking_response.success:
                return tracking_response
            
            tracking_response.reference_number = reference_number
            tracking_response.shipment_id = shipment.id
            
            logger.info(f"ShipmentTrackingService: Successfully tracked shipment for reference {reference_number}")
            return tracking_response
            
        except Exception as e:
            logger.error(f"ShipmentTrackingService: Error tracking shipment for reference {reference_number}: {str(e)}")
            return TrackingResponse.create_error_response(
                f'Internal server error: {str(e)}',
                'INTERNAL_ERROR'
            )
