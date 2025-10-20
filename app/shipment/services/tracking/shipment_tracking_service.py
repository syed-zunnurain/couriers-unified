"""Service for orchestrating shipment tracking operations."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from ..shipments.shipment_lookup_service import ShipmentLookupService
from ..status.shipment_status_service import ShipmentStatusService
from ..mapping.status_mapping_service import StatusMappingService
from ...schemas.tracking_response import TrackingResponse, TrackingLocation, TrackingEvent, TrackingDetails

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
        Track shipment by reference number using shipment status table.
        
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
            
            # Get status information from shipment status table
            status_summary = ShipmentStatusService.get_status_summary(shipment)
            latest_status = ShipmentStatusService.get_latest_status(shipment)
            
            if not latest_status:
                return TrackingResponse.create_error_response(
                    'No status information available for this shipment',
                    'NO_STATUS_FOUND'
                )
            
            # Build tracking response from status data
            tracking_response = self._build_tracking_response_from_status(shipment, status_summary)
            
            logger.info(f"ShipmentTrackingService: Successfully tracked shipment for reference {reference_number}")
            return tracking_response
            
        except Exception as e:
            logger.error(f"ShipmentTrackingService: Error tracking shipment for reference {reference_number}: {str(e)}")
            return TrackingResponse.create_error_response(
                f'Internal server error: {str(e)}',
                'INTERNAL_ERROR'
            )
    
    def _build_tracking_response_from_status(self, shipment, status_summary: dict) -> TrackingResponse:
        """Build TrackingResponse from shipment status data."""
        
        # Get latest status
        latest_status = ShipmentStatusService.get_latest_status(shipment)
        
        # Build current location from latest status
        current_location = TrackingLocation(
            address=latest_status.address or '',
            country=latest_status.country or '',
            postal_code=latest_status.postal_code or ''
        )
        
        # Build events from status history
        events = []
        for status_entry in status_summary['status_history']:
            location = TrackingLocation(
                address=status_entry['address'] or '',
                country=status_entry['country'] or '',
                postal_code=status_entry['postal_code'] or ''
            )
            
            event = TrackingEvent(
                timestamp=status_entry['created_at'].isoformat() if status_entry['created_at'] else '',
                status=status_entry['status'],
                description=status_entry['status_display'],
                location=location
            )
            events.append(event)
        
        # Build origin and destination from shipment data
        origin = TrackingLocation(
            address=shipment.shipper.address if shipment.shipper else '',
            country=shipment.shipper.country if shipment.shipper else '',
            postal_code=shipment.shipper.postal_code if shipment.shipper else '',
            city=shipment.shipper.city if shipment.shipper else ''
        )
        
        destination = TrackingLocation(
            address=shipment.consignee.address if shipment.consignee else '',
            country=shipment.consignee.country if shipment.consignee else '',
            postal_code=shipment.consignee.postal_code if shipment.consignee else '',
            city=shipment.consignee.city if shipment.consignee else ''
        )
        
        return TrackingResponse(
            success=True,
            tracking_number='',  # Remove tracking number from response
            service=shipment.courier.name if shipment.courier else '',
            current_status=latest_status.status,
            status_description=StatusMappingService.get_status_display_name(latest_status.status),
            current_location=current_location,
            events=events,
            origin=origin,
            destination=destination,
            details=TrackingDetails('', {}, []),  # Empty details object
            reference_number=shipment.reference_number,
            shipment_id=shipment.id
        )
