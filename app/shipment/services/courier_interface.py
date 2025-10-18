from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CourierRequest:
    """Standardized request format for all couriers."""
    shipment_type: str
    origin: str
    destination: str
    weight: float
    dimensions: Dict[str, float]  # {'length': 40, 'width': 30, 'height': 20}
    items: list
    pickup_date: str
    special_instructions: Optional[str] = None
    reference_number: str = None


@dataclass
class CourierResponse:
    """Standardized response format for all couriers."""
    success: bool
    tracking_number: Optional[str] = None
    courier_reference: Optional[str] = None
    estimated_delivery: Optional[str] = None
    cost: Optional[float] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class CourierInterface(ABC):
    """Abstract base class that all courier implementations must follow."""
    
    def __init__(self, courier_name: str, config: Dict[str, Any]):
        self.courier_name = courier_name
        self.config = config
    
    @abstractmethod
    def create_shipment(self, request: CourierRequest) -> CourierResponse:
        """
        Create a shipment with the courier.
        
        Args:
            request: Standardized courier request
            
        Returns:
            Standardized courier response
        """
        pass
    
    def __str__(self):
        return f"{self.courier_name} Courier"
