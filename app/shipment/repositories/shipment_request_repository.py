from typing import List, Optional
from django.utils import timezone
from ..models import ShipmentRequest
from .base_repository import DjangoRepository


class ShipmentRequestRepository(DjangoRepository):
    """Repository for ShipmentRequest model operations."""
    
    def __init__(self):
        super().__init__(ShipmentRequest)
    
    def get_by_reference_number(self, reference_number: str) -> Optional[ShipmentRequest]:
        """Get shipment request by reference number."""
        return self.first(reference_number=reference_number)
    
    def get_latest_by_reference_number(self, reference_number: str) -> Optional[ShipmentRequest]:
        """Get the latest shipment request by reference number ordered by created_at."""
        try:
            return self.model.objects.filter(
                reference_number=reference_number
            ).order_by('-created_at').first()
        except self.model.DoesNotExist:
            return None
    
    def get_pending_requests(self, limit: int = 10) -> List[ShipmentRequest]:
        """Get pending shipment requests."""
        return list(self.model.objects.filter(status='pending').order_by('created_at')[:limit])
    
    def get_processing_requests(self) -> List[ShipmentRequest]:
        """Get processing shipment requests."""
        return self.filter(status='processing')
    
    def get_failed_requests(self, max_retries: int = 3) -> List[ShipmentRequest]:
        """Get failed shipment requests that haven't exceeded max retries."""
        return self.filter(
            status='failed',
            retries__lt=max_retries
        )
    
    def get_requests_to_process(self, batch_size: int = 10) -> List[ShipmentRequest]:
        """Get requests that are pending or failed (with retries < 3)."""
        return list(
            self.model.objects.filter(
                status__in=['pending', 'failed'],
                retries__lt=3
            ).order_by('created_at')[:batch_size]
        )
    
    def get_by_status(self, status: str) -> List[ShipmentRequest]:
        """Get shipment requests by status."""
        return self.filter(status=status)
    
    def get_requests_by_date_range(self, start_date, end_date) -> List[ShipmentRequest]:
        """Get shipment requests created within a date range."""
        return self.filter(created_at__date__range=[start_date, end_date])
    
    def update_status(
        self,
        request_id: int,
        status: str,
        failed_reason: str = None,
        retries: int = None
    ) -> Optional[ShipmentRequest]:
        """Update shipment request status and related fields."""
        update_data = {'status': status}
        
        if failed_reason is not None:
            update_data['failed_reason'] = failed_reason
        
        if retries is not None:
            update_data['retries'] = retries
            update_data['last_retried_at'] = timezone.now()
        
        return self.update(request_id, **update_data)
    
    def mark_as_processing(self, request_id: int) -> Optional[ShipmentRequest]:
        """Mark a shipment request as processing."""
        return self.update_status(
            request_id=request_id,
            status='processing',
            retries=self.get_by_id(request_id).retries + 1 if self.get_by_id(request_id) else 0
        )
    
    def mark_as_completed(self, request_id: int) -> Optional[ShipmentRequest]:
        """Mark a shipment request as completed."""
        return self.update_status(request_id=request_id, status='completed')
    
    def mark_as_failed(self, request_id: int, failed_reason: str) -> Optional[ShipmentRequest]:
        """Mark a shipment request as failed."""
        return self.update_status(
            request_id=request_id,
            status='failed',
            failed_reason=failed_reason
        )
    
    def get_requests_by_retry_count(self, retry_count: int) -> List[ShipmentRequest]:
        """Get shipment requests with specific retry count."""
        return self.filter(retries=retry_count)
    
    def get_old_failed_requests(self, days_old: int = 7) -> List[ShipmentRequest]:
        """Get failed requests older than specified days."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days_old)
        return self.filter(
            status='failed',
            created_at__lt=cutoff_date
        )
    
    def exists_by_reference_number(self, reference_number: str) -> bool:
        """Check if a shipment request exists with the given reference number."""
        return self.exists(reference_number=reference_number)
    
    def get_recent_requests(self, limit: int = 10) -> List[ShipmentRequest]:
        """Get recent shipment requests ordered by created_at."""
        return list(self.model.objects.order_by('-created_at')[:limit])
