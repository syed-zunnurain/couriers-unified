import logging
from typing import Dict, Any, Optional
from django.db import transaction
from ...models import Shipment, ShipmentStatus
from ...services.shipments.shipment_lookup_service import ShipmentLookupService
from ...schemas.cancellation_response import CancellationResponse
from .courier_cancellation_service import CourierCancellationService

logger = logging.getLogger(__name__)


class ShipmentCancellationService:
    def __init__(self, 
                 lookup_service: ShipmentLookupService = None,
                 courier_cancellation_service: CourierCancellationService = None):
        self._lookup_service = lookup_service or ShipmentLookupService()
        self._courier_cancellation_service = courier_cancellation_service or CourierCancellationService()
    
    def cancel_shipment_by_reference(self, reference_number: str) -> CancellationResponse:
        try:
            logger.info(f"ShipmentCancellationService: Cancelling shipment for reference {reference_number}")
            
            shipment = self._lookup_service.get_shipment_by_reference(reference_number)
            if not shipment:
                return CancellationResponse.create_error_response(
                    'Shipment not found',
                    'SHIPMENT_NOT_FOUND'
                )
            
            if not self._courier_supports_cancellation(shipment):
                return CancellationResponse.create_error_response(
                    f'Courier {shipment.courier.name} does not support cancellation',
                    'CANCELLATION_NOT_SUPPORTED'
                )
            
            status_check = self._check_shipment_cancellable(shipment)
            if not status_check.success:
                return status_check
            
            # Cancel with courier
            courier_result = self._courier_cancellation_service.cancel_with_courier(shipment)
            if not courier_result.success:
                return courier_result
            
            # Update database
            with transaction.atomic():
                self._update_shipment_status(shipment)
                logger.info(f"ShipmentCancellationService: Successfully cancelled shipment {reference_number}")
                
                return CancellationResponse.create_success_response(
                    'Shipment cancelled successfully',
                    shipment.id,
                    shipment.reference_number,
                    shipment.courier_external_id
                )
                
        except Exception as e:
            logger.error(f"ShipmentCancellationService: Error cancelling shipment {reference_number}: {str(e)}")
            return CancellationResponse.create_error_response(
                f'Error cancelling shipment: {str(e)}',
                'CANCELLATION_ERROR'
            )
    
    def _courier_supports_cancellation(self, shipment: Shipment) -> bool:
        """Check if the courier supports cancellation."""
        try:
            return shipment.courier.supports_cancellation
        except Exception as e:
            logger.error(f"ShipmentCancellationService: Error checking cancellation support: {str(e)}")
            return False
    
    def _check_shipment_cancellable(self, shipment: Shipment) -> CancellationResponse:
        """Check if shipment can be cancelled based on its status."""
        try:
            latest_status = ShipmentStatus.objects.filter(
                shipment=shipment
            ).order_by('-created_at').first()
            
            if not latest_status:
                return CancellationResponse.create_error_response(
                    'No status found for shipment',
                    'NO_STATUS_FOUND'
                )
            
            non_cancellable_statuses = ['completed', 'in_transit', 'delivered', 'cancelled']
            if latest_status.status in non_cancellable_statuses:
                return CancellationResponse.create_error_response(
                    f'Cannot cancel shipment with status: {latest_status.status}',
                    'STATUS_NOT_CANCELLABLE'
                )
            
            return CancellationResponse(
                success=True,
                message='Shipment can be cancelled'
            )
            
        except Exception as e:
            logger.error(f"ShipmentCancellationService: Error checking shipment status: {str(e)}")
            return CancellationResponse.create_error_response(
                f'Error checking shipment status: {str(e)}',
                'STATUS_CHECK_ERROR'
            )
    
    def _update_shipment_status(self, shipment: Shipment) -> None:
        """Update shipment status to cancelled."""
        try:
            from ...services.status.shipment_status_service import ShipmentStatusService
            
            ShipmentStatusService.create_status(
                shipment=shipment,
                status='cancelled'
            )
            
        except Exception as e:
            logger.error(f"ShipmentCancellationService: Error updating shipment status: {str(e)}")
            raise
