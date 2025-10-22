from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Weight:
    value: float
    unit: str
    
    def to_kg(self) -> float:
        if self.unit.lower() in ['kg', 'kilogram', 'kilograms']:
            return self.value
        else:
            raise ValueError(f"Unsupported weight unit: {self.unit}")


@dataclass
class Dimensions:
    height: float
    width: float
    length: float
    unit: str
    
    def to_cm(self) -> 'Dimensions':
        if self.unit.lower() in ['mm', 'millimeter', 'millimeters']:
            return self
        else:
            raise ValueError(f"Unsupported dimension unit: {self.unit}")


@dataclass
class CourierRequest:
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
    success: bool
    tracking_number: Optional[str] = None
    courier_reference: Optional[str] = None
    estimated_delivery: Optional[str] = None
    cost: Optional[float] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
