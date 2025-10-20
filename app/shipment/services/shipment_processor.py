import logging
from .request_batch_processor import RequestBatchProcessor

logger = logging.getLogger(__name__)


class ShipmentProcessor:
    """Main service class for processing shipment requests - now follows SOLID principles."""
    
    def __init__(self, batch_processor: RequestBatchProcessor = None):
        self.batch_processor = batch_processor or RequestBatchProcessor()
    
    def process_requests(self, batch_size=10):
        """Process a batch of shipment requests - delegates to batch processor."""
        return self.batch_processor.process_requests(batch_size)
    
    def get_requests_to_process(self, batch_size):
        """Get shipment requests that need processing - delegates to batch processor."""
        return self.batch_processor.get_requests_to_process(batch_size)
    
    def process_single_request(self, request):
        """Process a single shipment request - delegates to request processor."""
        from .request_processor import RequestProcessor
        processor = RequestProcessor()
        return processor.process_single_request(request)
