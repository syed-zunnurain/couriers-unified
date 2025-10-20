"""Unified label response schema for all couriers."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LabelResponse:
    """Unified label response for all couriers."""
    success: bool
    id: Optional[int] = None
    reference_number: Optional[str] = None
    url: Optional[str] = None
    format: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'LabelResponse':
        """Create LabelResponse from dictionary."""
        return cls(
            success=data.get('success', False),
            id=data.get('id'),
            reference_number=data.get('reference_number'),
            url=data.get('url'),
            format=data.get('format'),
            is_active=data.get('is_active'),
            created_at=data.get('created_at'),
            error=data.get('error'),
            error_code=data.get('error_code')
        )

    def to_dict(self) -> dict:
        """Convert LabelResponse to dictionary."""
        result = {
            'success': self.success
        }
        
        if self.success:
            if self.id is not None:
                result['id'] = self.id
            if self.reference_number is not None:
                result['reference_number'] = self.reference_number
            if self.url is not None:
                result['url'] = self.url
            if self.format is not None:
                result['format'] = self.format
            if self.is_active is not None:
                result['is_active'] = self.is_active
            if self.created_at is not None:
                result['created_at'] = self.created_at
        else:
            if self.error is not None:
                result['error'] = self.error
            if self.error_code is not None:
                result['error_code'] = self.error_code
        
        return result

    @classmethod
    def create_success_response(cls, id: int, reference_number: str, url: str, 
                              format: str, is_active: bool, created_at: str) -> 'LabelResponse':
        """Create successful label response."""
        return cls(
            success=True,
            id=id,
            reference_number=reference_number,
            url=url,
            format=format,
            is_active=is_active,
            created_at=created_at
        )

    @classmethod
    def create_error_response(cls, error: str, error_code: str) -> 'LabelResponse':
        """Create error label response."""
        return cls(
            success=False,
            error=error,
            error_code=error_code
        )
