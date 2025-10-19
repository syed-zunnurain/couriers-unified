"""Base mapping interfaces for courier-specific implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ....schemas.shipment_request import ShipmentRequest
from ....schemas.shipment_response import ShipmentResponse


class BaseStatusMapper(ABC):
    """Base interface for status mapping."""
    
    @abstractmethod
    def map_status(self, courier_status: str) -> str:
        """Map courier-specific status to standardized status."""
        pass
    
    @abstractmethod
    def get_supported_statuses(self) -> list:
        """Get list of supported courier statuses."""
        pass


class BaseProductMapper(ABC):
    """Base interface for product type mapping."""
    
    @abstractmethod
    def map_product_type(self, courier_product_code: str) -> str:
        """Map courier product code to standardized shipment type."""
        pass
    
    @abstractmethod
    def map_shipment_type_to_courier_product(self, shipment_type: str) -> str:
        """Map standardized shipment type to courier product code."""
        pass
    
    @abstractmethod
    def get_supported_products(self) -> list:
        """Get list of supported courier product codes."""
        pass


class BaseResponseMapper(ABC):
    """Base interface for response mapping."""
    
    @abstractmethod
    def map_response(self, courier_response: Dict[str, Any], success: bool = True) -> ShipmentResponse:
        """Map courier response to standardized ShipmentResponse."""
        pass


class BasePayloadBuilder(ABC):
    """Base interface for payload building."""
    
    @abstractmethod
    def build_payload(self, request: ShipmentRequest) -> Dict[str, Any]:
        """Build courier-specific payload from standardized request."""
        pass
    
    @abstractmethod
    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """Validate courier payload structure."""
        pass
