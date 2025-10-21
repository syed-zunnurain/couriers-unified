import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DHLProductMapper:
    DHL_PRODUCT_MAPPING = {
        'V01PAK': 'NORMAL',
        'V53WPAK': 'URGENT',
        'V54EPAK': 'SAME_DAY_DELIVERY',
    }
    
    DHL_SHIPMENT_TYPE_MAPPING = {
        'NORMAL': 'V01PAK',
        'URGENT': 'V53WPAK',
        'SAME_DAY_DELIVERY': 'V54EPAK',
    }
    
    @classmethod
    def map_dhl_product_type(cls, product_code: str) -> str:
        return cls.DHL_PRODUCT_MAPPING.get(product_code, 'standard')
    
    @classmethod
    def map_shipment_type_to_dhl_product(cls, shipment_type: str) -> str:
        return cls.DHL_SHIPMENT_TYPE_MAPPING.get(shipment_type.lower(), 'V01PAK')
    
    @classmethod
    def get_supported_products(cls) -> list:
        return list(cls.DHL_PRODUCT_MAPPING.keys())
    
    @classmethod
    def get_supported_shipment_types(cls) -> list:
        return list(cls.DHL_SHIPMENT_TYPE_MAPPING.keys())
