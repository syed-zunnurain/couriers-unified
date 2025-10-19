from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class ShipmentResponse:
    """Schema for shipment creation response."""
    success: bool
    tracking_number: Optional[str] = None
    courier_reference: Optional[str] = None
    estimated_delivery: Optional[str] = None
    cost: Optional[float] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


@dataclass
class TrackingInfo:
    """Schema for tracking information."""
    tracking_number: str
    status: str
    current_location: Optional[str] = None
    estimated_delivery: Optional[str] = None
    last_updated: Optional[datetime] = None
    events: Optional[list] = None


@dataclass
class ShipmentStatus:
    """Schema for shipment status."""
    status: str
    description: str
    timestamp: datetime
    location: Optional[str] = None
    notes: Optional[str] = None
