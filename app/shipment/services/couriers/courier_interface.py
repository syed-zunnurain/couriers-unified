from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Weight:
    """Represents weight with value and unit."""
    value: float
    unit: str
    
    def to_kg(self) -> float:
        """Convert weight to kilograms."""
        if self.unit.lower() in ['kg', 'kilogram', 'kilograms']:
            return self.value
        else:
            raise ValueError(f"Unsupported weight unit: {self.unit}")


@dataclass
class Dimensions:
    """Represents dimensions with height, width, length and unit."""
    height: float
    width: float
    length: float
    unit: str
    
    def to_cm(self) -> 'Dimensions':
        """Convert dimensions to centimeters."""
        if self.unit.lower() in ['mm', 'millimeter', 'millimeters']:
            return self
        else:
            raise ValueError(f"Unsupported dimension unit: {self.unit}")


@dataclass
class CourierRequest:
    """Standardized request format for all couriers."""
    shipment_type: str
    reference_number: str
    shipper: 'Shipper'
    consignee: 'Consignee'
    route: 'Route'
    weight: Weight
    dimensions: Dimensions
    pickup_date: Optional[str] = None
    special_instructions: Optional[str] = None

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
