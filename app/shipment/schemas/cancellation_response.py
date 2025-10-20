from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class CancellationResponse:
    """Schema for shipment cancellation response."""
    success: bool
    message: str
    shipment_id: Optional[int] = None
    reference_number: Optional[str] = None
    courier_external_id: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert CancellationResponse to dictionary."""
        result = {
            'success': self.success,
            'message': self.message
        }
        
        if self.success:
            result['data'] = {
                'shipment_id': self.shipment_id,
                'reference_number': self.reference_number,
                'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None
            }
        else:
            result['error_code'] = self.error_code
            if self.error_message:
                result['error_message'] = self.error_message
        
        if self.raw_response:
            result['raw_response'] = self.raw_response
            
        return result

    @classmethod
    def create_success_response(cls, 
                              message: str,
                              shipment_id: int,
                              reference_number: str,
                              courier_external_id: Optional[str] = None,
                              raw_response: Optional[Dict[str, Any]] = None) -> 'CancellationResponse':
        """Create a successful cancellation response."""
        return cls(
            success=True,
            message=message,
            shipment_id=shipment_id,
            reference_number=reference_number,
            courier_external_id=courier_external_id,
            cancelled_at=datetime.utcnow(),
            raw_response=raw_response
        )

    @classmethod
    def create_error_response(cls, 
                            message: str,
                            error_code: str,
                            error_message: Optional[str] = None,
                            raw_response: Optional[Dict[str, Any]] = None) -> 'CancellationResponse':
        """Create an error cancellation response."""
        return cls(
            success=False,
            message=message,
            error_code=error_code,
            error_message=error_message,
            raw_response=raw_response
        )
