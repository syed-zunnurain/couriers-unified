"""Service for processing batches of shipment requests."""

import logging
from typing import List, Dict, Any
from ...repositories.repository_factory import repositories

logger = logging.getLogger(__name__)


class RequestBatchProcessor:
    """Handles batch processing of shipment requests following SRP."""
    
    def __init__(self, request_processor=None):
        self._request_processor = request_processor
    
    @property
    def request_processor(self):
        if self._request_processor is None:
            from .request_processor import RequestProcessor
            self._request_processor = RequestProcessor()
        return self._request_processor
    
    def process_requests(self, batch_size: int = 10) -> Dict[str, Any]:
        """Process a batch of shipment requests."""
        logger.info(f"RequestBatchProcessor: Starting to process requests with batch_size={batch_size}")
        requests_to_process = self.get_requests_to_process(batch_size)
        logger.info(f"RequestBatchProcessor: Found {len(requests_to_process)} requests to process")
        
        results = {
            'total': len(requests_to_process),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for request in requests_to_process:
            logger.info(f"RequestBatchProcessor: Processing request ID={request.id}, reference={request.reference_number}")
            try:
                result = self.request_processor.process_single_request(request)
                results['details'].append(result)
                
                if result['success']:
                    results['successful'] += 1
                    logger.info(f"RequestBatchProcessor: Successfully processed request ID={request.id}")
                else:
                    results['failed'] += 1
                    logger.warning(f"RequestBatchProcessor: Failed to process request ID={request.id}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f'RequestBatchProcessor: Error processing request {request.id}: {str(e)}')
                results['failed'] += 1
                results['details'].append({
                    'request_id': request.id,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_requests_to_process(self, batch_size: int) -> List:
        """Get shipment requests that need processing."""
        return repositories.shipment_request.get_requests_to_process(batch_size)
