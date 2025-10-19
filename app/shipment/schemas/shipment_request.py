from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date


@dataclass
class Weight:
    """Represents weight with value and unit."""
    value: float
    unit: str
    
    def to_kg(self) -> float:
        """Convert weight to kilograms."""
        if self.unit.lower() in ['kg', 'kilogram', 'kilograms']:
            return self.value
        elif self.unit.lower() in ['lb', 'lbs', 'pound', 'pounds']:
            return self.value * 0.453592
        elif self.unit.lower() in ['g', 'gram', 'grams']:
            return self.value / 1000
        else:
            raise ValueError(f"Unsupported weight unit: {self.unit}")
    
    def to_lb(self) -> float:
        """Convert weight to pounds."""
        if self.unit.lower() in ['lb', 'lbs', 'pound', 'pounds']:
            return self.value
        elif self.unit.lower() in ['kg', 'kilogram', 'kilograms']:
            return self.value * 2.20462
        elif self.unit.lower() in ['g', 'gram', 'grams']:
            return (self.value / 1000) * 2.20462
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
        if self.unit.lower() in ['cm', 'centimeter', 'centimeters']:
            return self
        elif self.unit.lower() in ['in', 'inch', 'inches']:
            return Dimensions(
                height=self.height * 2.54,
                width=self.width * 2.54,
                length=self.length * 2.54,
                unit='cm'
            )
        elif self.unit.lower() in ['m', 'meter', 'meters']:
            return Dimensions(
                height=self.height * 100,
                width=self.width * 100,
                length=self.length * 100,
                unit='cm'
            )
        else:
            raise ValueError(f"Unsupported dimension unit: {self.unit}")
    
    def to_inches(self) -> 'Dimensions':
        """Convert dimensions to inches."""
        if self.unit.lower() in ['in', 'inch', 'inches']:
            return self
        elif self.unit.lower() in ['cm', 'centimeter', 'centimeters']:
            return Dimensions(
                height=self.height / 2.54,
                width=self.width / 2.54,
                length=self.length / 2.54,
                unit='in'
            )
        elif self.unit.lower() in ['m', 'meter', 'meters']:
            return Dimensions(
                height=(self.height * 100) / 2.54,
                width=(self.width * 100) / 2.54,
                length=(self.length * 100) / 2.54,
                unit='in'
            )
        else:
            raise ValueError(f"Unsupported dimension unit: {self.unit}")
    
    @property
    def volume(self) -> float:
        """Calculate volume in cubic units."""
        return self.height * self.width * self.length


@dataclass
class Address:
    """Represents an address."""
    name: str
    address: str
    city: str
    country: str
    phone: str
    email: str
    postal_code: Optional[str] = None


@dataclass
class Route:
    """Represents a shipping route."""
    origin: str
    destination: str
    id: Optional[int] = None


@dataclass
class ShipmentRequest:
    """Schema for shipment creation request."""
    shipment_type: str
    reference_number: str
    shipper: Address
    consignee: Address
    route: Route
    weight: Weight
    dimensions: Dimensions
    pickup_date: Optional[date] = None
    special_instructions: Optional[str] = None
    items: Optional[list] = None
