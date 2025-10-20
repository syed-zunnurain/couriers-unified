"""Unified tracking response schema for all couriers."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class TrackingLocation:
    """Standardized location information."""
    address: str
    city: str
    country: str
    postal_code: str


@dataclass
class TrackingEvent:
    """Standardized tracking event."""
    timestamp: str
    status: str
    description: str
    location: TrackingLocation


@dataclass
class TrackingDetails:
    """Standardized tracking details."""
    product_name: str
    weight: Dict[str, Any]
    references: List[Dict[str, str]]


@dataclass
class TrackingResponse:
    """Unified tracking response for all couriers."""
    success: bool
    tracking_number: str
    service: str
    current_status: str
    status_description: str
    current_location: TrackingLocation
    events: List[TrackingEvent]
    origin: TrackingLocation
    destination: TrackingLocation
    details: TrackingDetails
    reference_number: Optional[str] = None
    shipment_id: Optional[int] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackingResponse':
        """Create TrackingResponse from dictionary."""
        events = []
        for event_data in data.get('events', []):
            location_data = event_data.get('location', {})
            location = TrackingLocation(
                address=location_data.get('address', ''),
                city=location_data.get('city', ''),
                country=location_data.get('country', ''),
                postal_code=location_data.get('postal_code', '')
            )
            
            event = TrackingEvent(
                timestamp=event_data.get('timestamp', ''),
                status=event_data.get('status', 'UNKNOWN'),
                description=event_data.get('description', ''),
                location=location
            )
            events.append(event)

        current_location_data = data.get('current_location', {})
        current_location = TrackingLocation(
            address=current_location_data.get('address', ''),
            city=current_location_data.get('city', ''),
            country=current_location_data.get('country', ''),
            postal_code=current_location_data.get('postal_code', '')
        )

        origin_data = data.get('origin', {})
        origin = TrackingLocation(
            address=origin_data.get('address', ''),
            city=origin_data.get('city', ''),
            country=origin_data.get('country', ''),
            postal_code=origin_data.get('postal_code', '')
        )

        destination_data = data.get('destination', {})
        destination = TrackingLocation(
            address=destination_data.get('address', ''),
            city=destination_data.get('city', ''),
            country=destination_data.get('country', ''),
            postal_code=destination_data.get('postal_code', '')
        )

        details_data = data.get('details', {})
        details = TrackingDetails(
            product_name=details_data.get('product_name', ''),
            weight=details_data.get('weight', {}),
            references=details_data.get('references', [])
        )

        return cls(
            success=data.get('success', False),
            tracking_number=data.get('tracking_number', ''),
            service=data.get('service', ''),
            current_status=data.get('current_status', 'UNKNOWN'),
            status_description=data.get('status_description', ''),
            current_location=current_location,
            events=events,
            origin=origin,
            destination=destination,
            details=details,
            reference_number=data.get('reference_number'),
            shipment_id=data.get('shipment_id'),
            error=data.get('error'),
            error_code=data.get('error_code')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert TrackingResponse to dictionary."""
        return {
            'success': self.success,
            'tracking_number': self.tracking_number,
            'service': self.service,
            'current_status': self.current_status,
            'status_description': self.status_description,
            'current_location': {
                'address': self.current_location.address,
                'city': self.current_location.city,
                'country': self.current_location.country,
                'postal_code': self.current_location.postal_code
            },
            'events': [
                {
                    'timestamp': event.timestamp,
                    'status': event.status,
                    'description': event.description,
                    'location': {
                        'address': event.location.address,
                        'city': event.location.city,
                        'country': event.location.country,
                        'postal_code': event.location.postal_code
                    }
                }
                for event in self.events
            ],
            'origin': {
                'address': self.origin.address,
                'city': self.origin.city,
                'country': self.origin.country,
                'postal_code': self.origin.postal_code
            },
            'destination': {
                'address': self.destination.address,
                'city': self.destination.city,
                'country': self.destination.country,
                'postal_code': self.destination.postal_code
            },
            'details': {
                'product_name': self.details.product_name,
                'weight': self.details.weight,
                'references': self.details.references
            },
            'reference_number': self.reference_number,
            'shipment_id': self.shipment_id,
            'error': self.error,
            'error_code': self.error_code
        }

    @classmethod
    def create_error_response(cls, error: str, error_code: str) -> 'TrackingResponse':
        """Create error response."""
        empty_location = TrackingLocation('', '', '', '')
        empty_details = TrackingDetails('', {}, [])
        
        return cls(
            success=False,
            tracking_number='',
            service='',
            current_status='UNKNOWN',
            status_description='',
            current_location=empty_location,
            events=[],
            origin=empty_location,
            destination=empty_location,
            details=empty_details,
            error=error,
            error_code=error_code
        )
