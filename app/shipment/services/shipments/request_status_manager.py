import logging
from ...repositories.repository_factory import repositories

logger = logging.getLogger(__name__)


class RequestStatusManager:
    def __init__(self):
        self._shipment_request_repo = repositories.shipment_request
    
    def mark_as_processing(self, request) -> None:
        updated_request = self._shipment_request_repo.mark_as_processing(request.id)
        if updated_request:
            logger.info(f"RequestStatusManager: Updated request ID={request.id} status to processing, retries={updated_request.retries}")
        else:
            logger.error(f"RequestStatusManager: Failed to update request ID={request.id} status to processing")
    
    def mark_as_completed(self, request) -> None:
        updated_request = self._shipment_request_repo.mark_as_completed(request.id)
        if updated_request:
            logger.info(f"RequestStatusManager: Updated request ID={request.id} status to completed")
        else:
            logger.error(f"RequestStatusManager: Failed to update request ID={request.id} status to completed")
    
    def mark_as_failed(self, request, reason: str) -> None:
        updated_request = self._shipment_request_repo.mark_as_failed(request.id, reason)
        if updated_request:
            logger.info(f"RequestStatusManager: Updated request ID={request.id} status to failed, reason={reason}")
        else:
            logger.error(f"RequestStatusManager: Failed to update request ID={request.id} status to failed, reason={reason}")
