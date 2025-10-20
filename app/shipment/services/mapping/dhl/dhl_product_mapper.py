"""DHL-specific product type mapping service."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DHLProductMapper:
    """Maps DHL-specific product types to standardized shipment types."""
    
    DHL_PRODUCT_MAPPING = {
        'V01PAK': 'NORMAL',                    # DHL Paket -> NORMAL
        'V53WPAK': 'URGENT',                   # DHL Express Paket -> URGENT
        'V54EPAK': 'SAME_DAY_DELIVERY',        # DHL Express Paket Plus -> SAME_DAY_DELIVERY
    }
    
    DHL_SHIPMENT_TYPE_MAPPING = {
        'NORMAL': 'V01PAK',                    # DHL Paket (standard)
        'URGENT': 'V53WPAK',                   # DHL Express Paket
        'SAME_DAY_DELIVERY': 'V54EPAK',        # DHL Express Paket Plus
    }
    
    @classmethod
    def map_dhl_product_type(cls, product_code: str) -> str:
        """Map DHL product code to standardized shipment type."""
        return cls.DHL_PRODUCT_MAPPING.get(product_code, 'standard')
    
    @classmethod
    def map_shipment_type_to_dhl_product(cls, shipment_type: str) -> str:
        """Map standardized shipment type to DHL product code."""
        return cls.DHL_SHIPMENT_TYPE_MAPPING.get(shipment_type.lower(), 'V01PAK')
    
    @classmethod
    def get_supported_products(cls) -> list:
        """Get list of supported DHL product codes."""
        return list(cls.DHL_PRODUCT_MAPPING.keys())
    
    @classmethod
    def get_supported_shipment_types(cls) -> list:
        """Get list of supported standardized shipment types for DHL."""
        return list(cls.DHL_SHIPMENT_TYPE_MAPPING.keys())
