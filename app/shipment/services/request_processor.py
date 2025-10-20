"""Service for processing individual shipment requests."""

import logging
from django.utils import timezone
from django.db import transaction
from typing import Dict, Any
from .courier_processor import CourierProcessor
from .request_status_manager import RequestStatusManager
from .request_data_converter import RequestDataConverter
from ..repositories.repository_factory import repositories

logger = logging.getLogger(__name__)


class RequestProcessor:
    """Handles processing of individual shipment requests following SRP."""
    
    def __init__(self, 
                 courier_processor: CourierProcessor = None,
                 status_manager: RequestStatusManager = None,
                 data_converter: RequestDataConverter = None):
        self.courier_processor = courier_processor or CourierProcessor()
        self.status_manager = status_manager or RequestStatusManager()
        self.data_converter = data_converter or RequestDataConverter()
    
    def process_single_request(self, request) -> Dict[str, Any]:
        """Process a single shipment request."""
        logger.info(f"RequestProcessor: Starting to process single request ID={request.id}")
        
        with transaction.atomic():
            # Update request status to processing
            self.status_manager.mark_as_processing(request)
            
            request_data = request.request_body
            logger.info(f"RequestProcessor: Request data for ID={request.id}: shipment_type_id={request_data.get('shipment_type_id')}")
            
            # Get shipper and consignee objects
            consignee = repositories.consignee.get_by_id(request_data.get('consignee_id'))
            shipper = repositories.shipper.get_by_id(request_data.get('shipper_id'))
            
            if not consignee or not shipper:
                error_msg = "Shipper or consignee not found"
                logger.error(f"RequestProcessor: {error_msg}")
                self.status_manager.mark_as_failed(request, error_msg)
                return {
                    'request_id': request.id,
                    'reference_number': request.reference_number,
                    'success': False,
                    'error': error_msg,
                    'courier': None
                }
            
            # Process with courier
            result = self.courier_processor.process_with_courier(
                request_data, 
                request.reference_number, 
                shipper, 
                consignee
            )
            
            # Update request status based on result
            if result['success']:
                self.status_manager.mark_as_completed(request)
                return {
                    'request_id': request.id,
                    'reference_number': request.reference_number,
                    'success': True,
                    'message': result['message'],
                    'courier': result.get('courier')
                }
            else:
                self.status_manager.mark_as_failed(request, result.get('error', 'Unknown error'))
                return {
                    'request_id': request.id,
                    'reference_number': request.reference_number,
                    'success': False,
                    'error': result['error'],
                    'courier': result.get('courier')
                }
