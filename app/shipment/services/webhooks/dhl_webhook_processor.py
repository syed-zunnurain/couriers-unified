"""DHL webhook processor following Single Responsibility Principle."""

import logging
from typing import Dict, Any, Optional
from django.db import transaction
from ...models import Shipment
from ...services.status.shipment_status_service import ShipmentStatusService
from ...services.mapping.status_mapping_service import StatusMappingService
from .dhl_webhook_parser import DHLWebhookData

logger = logging.getLogger(__name__)


class DHLWebhookProcessor:
    """
    Single Responsibility: Process validated DHL webhook data and update shipment status.
    
    This class only handles the business logic of processing webhook data.
    It doesn't parse, validate, or handle HTTP requests - just processes data.
    """
    
    def __init__(self):
        self._shipment_lookup_service = None
    
    @property
    def shipment_lookup_service(self):
        """Lazy load shipment lookup service."""
        if not self._shipment_lookup_service:
            from ...services.shipments.shipment_lookup_service import ShipmentLookupService
            self._shipment_lookup_service = ShipmentLookupService()
        return self._shipment_lookup_service
    
    def process_webhook(self, webhook_data: DHLWebhookData) -> Dict[str, Any]:
        """
        Process DHL webhook data and update shipment status.
        
        Args:
            webhook_data: Parsed and validated webhook data
            
        Returns:
            Dict containing processing result
        """
        try:
            logger.info(f"DHLWebhookProcessor: Processing webhook for tracking number {webhook_data.tracking_number}")
            
            # Find shipment by courier external ID
            shipment = self._find_shipment_by_tracking_number(webhook_data.tracking_number)
            if not shipment:
                logger.warning(f"DHLWebhookProcessor: Shipment not found for tracking number {webhook_data.tracking_number}")
                return {
                    'success': False,
                    'message': 'Shipment not found',
                    'error_code': 'SHIPMENT_NOT_FOUND'
                }
            
            # Check if shipment is already cancelled
            if self._is_shipment_cancelled(shipment):
                logger.info(f"DHLWebhookProcessor: Shipment {shipment.reference_number} is already cancelled, ignoring webhook")
                return {
                    'success': True,
                    'message': 'Shipment already cancelled, webhook ignored',
                    'shipment_id': shipment.id,
                    'reference_number': shipment.reference_number,
                    'status_entry_id': None,
                    'mapped_status': None,
                    'status': 'cancelled_ignored'
                }
            
            # Map DHL status to our standardized status
            standardized_status = self._map_dhl_status(webhook_data.status)
            
            # Check for duplicate status before updating
            if self._is_duplicate_status(shipment, standardized_status):
                logger.info(f"DHLWebhookProcessor: Duplicate status '{standardized_status}' for shipment {shipment.reference_number}, ignoring webhook")
                return {
                    'success': True,
                    'message': 'Duplicate status ignored',
                    'shipment_id': shipment.id,
                    'reference_number': shipment.reference_number,
                    'status_entry_id': None,
                    'mapped_status': None,
                    'status': 'duplicate_ignored'
                }
            
            # Update shipment status in database
            status_entry = self._update_shipment_status(
                shipment=shipment,
                dhl_status=webhook_data.status,
                standardized_status=standardized_status,
                webhook_data=webhook_data
            )
            
            logger.info(f"DHLWebhookProcessor: Successfully processed webhook for shipment {shipment.reference_number}")
            return {
                'success': True,
                'message': 'Webhook processed successfully',
                'shipment_id': shipment.id,
                'reference_number': shipment.reference_number,
                'status_entry_id': status_entry.id,
                'mapped_status': standardized_status
            }
            
        except Exception as e:
            logger.error(f"DHLWebhookProcessor: Error processing webhook: {str(e)}")
            return {
                'success': False,
                'message': f'Error processing webhook: {str(e)}',
                'error_code': 'PROCESSING_ERROR'
            }
    
    def _find_shipment_by_tracking_number(self, tracking_number: str) -> Optional[Shipment]:
        """
        Find shipment by DHL tracking number (courier_external_id).
        
        Args:
            tracking_number: DHL tracking number
            
        Returns:
            Shipment object if found, None otherwise
        """
        try:
            logger.info(f"DHLWebhookProcessor: Looking up shipment with courier_external_id: {tracking_number}")
            
            shipment = Shipment.objects.filter(
                courier_external_id=tracking_number
            ).first()
            
            if shipment:
                logger.info(f"DHLWebhookProcessor: Found shipment {shipment.reference_number} for tracking number {tracking_number}")
            else:
                logger.warning(f"DHLWebhookProcessor: No shipment found for tracking number {tracking_number}")
            
            return shipment
            
        except Exception as e:
            logger.error(f"DHLWebhookProcessor: Error looking up shipment: {str(e)}")
            return None
    
    def _map_dhl_status(self, dhl_status: str) -> str:
        """
        Map DHL status to our standardized status.
        
        Args:
            dhl_status: Raw DHL status
            
        Returns:
            Standardized status
        """
        try:
            standardized_status = StatusMappingService.map_courier_status('dhl', dhl_status)
            logger.info(f"DHLWebhookProcessor: Mapped DHL status '{dhl_status}' to '{standardized_status}'")
            return standardized_status
            
        except Exception as e:
            logger.error(f"DHLWebhookProcessor: Error mapping DHL status: {str(e)}")
            return 'unknown'
    
    def _update_shipment_status(self, 
                               shipment: Shipment, 
                               dhl_status: str, 
                               standardized_status: str,
                               webhook_data: DHLWebhookData) -> Any:
        """
        Update shipment status in database.
        
        Args:
            shipment: Shipment object
            dhl_status: Original DHL status
            standardized_status: Mapped standardized status
            webhook_data: Webhook data containing location info
            
        Returns:
            Created ShipmentStatus object
        """
        try:
            logger.info(f"DHLWebhookProcessor: Updating status for shipment {shipment.reference_number}")
            
            with transaction.atomic():
                # Create new status entry using the status service
                status_entry = ShipmentStatusService.create_status(
                    shipment=shipment,
                    status=standardized_status,
                    address=webhook_data.location_address,
                    postal_code=webhook_data.location_postal_code,
                    country=webhook_data.location_country
                )
                
                logger.info(f"DHLWebhookProcessor: Created status entry {status_entry.id} with status '{standardized_status}'")
                return status_entry
                
        except Exception as e:
            logger.error(f"DHLWebhookProcessor: Error updating shipment status: {str(e)}")
            raise
    
    def _is_duplicate_status(self, shipment: Shipment, standardized_status: str) -> bool:
        """
        Check if the same status already exists for the shipment.
        
        Args:
            shipment: Shipment object
            standardized_status: Standardized status to check
            
        Returns:
            True if duplicate status exists, False otherwise
        """
        try:
            from ...models import ShipmentStatus
            
            # Check if the same status already exists for this shipment
            existing_status = ShipmentStatus.objects.filter(
                shipment=shipment,
                status=standardized_status.lower()
            ).first()
            
            if existing_status:
                logger.info(f"DHLWebhookProcessor: Found existing status '{standardized_status}' for shipment {shipment.reference_number}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"DHLWebhookProcessor: Error checking for duplicate status: {str(e)}")
            # If there's an error checking for duplicates, we'll process the webhook anyway
            return False
    
    def _is_shipment_cancelled(self, shipment: Shipment) -> bool:
        """
        Check if the shipment is already cancelled.
        
        Args:
            shipment: Shipment object
            
        Returns:
            True if shipment is cancelled, False otherwise
        """
        try:
            from ...models import ShipmentStatus
            
            # Get the latest status for this shipment
            latest_status = ShipmentStatus.objects.filter(
                shipment=shipment
            ).order_by('-created_at').first()
            
            if latest_status and latest_status.status.lower() == 'cancelled':
                logger.info(f"DHLWebhookProcessor: Shipment {shipment.reference_number} has latest status 'cancelled'")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"DHLWebhookProcessor: Error checking if shipment is cancelled: {str(e)}")
            # If there's an error checking, we'll process the webhook anyway
            return False
    
    def get_webhook_summary(self, webhook_data: DHLWebhookData) -> Dict[str, Any]:
        """
        Get summary of webhook data for logging/debugging.
        
        Args:
            webhook_data: Parsed webhook data
            
        Returns:
            Dict containing webhook summary
        """
        return {
            'tracking_number': webhook_data.tracking_number,
            'status': webhook_data.status,
            'timestamp': webhook_data.timestamp,
            'location': {
                'address': webhook_data.location_address,
                'country': webhook_data.location_country,
                'postal_code': webhook_data.location_postal_code
            },
            'description': webhook_data.description
        }
