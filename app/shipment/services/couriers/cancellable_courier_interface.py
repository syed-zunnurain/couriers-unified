from abc import ABC, abstractmethod
from typing import Dict, Any


class CancellableCourierInterface(ABC):
    """Interface for couriers that support shipment cancellation."""
    
    @abstractmethod
    def cancel_shipment(self, courier_external_id: str) -> Dict[str, Any]:
        """
        Cancel a shipment with the courier.
        
        Args:
            courier_external_id: The courier's external ID for the shipment
            
        Returns:
            Dict containing cancellation result with 'success' and 'message' keys
        """
        pass
