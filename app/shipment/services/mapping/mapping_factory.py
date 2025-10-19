"""Factory for accessing courier-specific mapping services."""

from typing import Dict, Type
from .base_mapper import BaseStatusMapper, BaseProductMapper, BaseResponseMapper, BasePayloadBuilder
from .dhl.dhl_status_mapper import DHLStatusMapper
from .dhl.dhl_product_mapper import DHLProductMapper
from .dhl.dhl_response_mapper import DHLResponseMapper
from .dhl.dhl_payload_builder import DHLPayloadBuilder


class MappingFactory:
    """Factory class to provide access to courier-specific mapping services."""
    
    # Registry of courier-specific mappers
    STATUS_MAPPERS: Dict[str, Type[BaseStatusMapper]] = {
        'dhl': DHLStatusMapper,
    }
    
    PRODUCT_MAPPERS: Dict[str, Type[BaseProductMapper]] = {
        'dhl': DHLProductMapper,
    }
    
    RESPONSE_MAPPERS: Dict[str, Type[BaseResponseMapper]] = {
        'dhl': DHLResponseMapper,
    }
    
    PAYLOAD_BUILDERS: Dict[str, Type[BasePayloadBuilder]] = {
        'dhl': DHLPayloadBuilder,
    }
    
    @classmethod
    def get_status_mapper(cls, courier: str) -> BaseStatusMapper:
        """Get status mapper for specific courier."""
        mapper_class = cls.STATUS_MAPPERS.get(courier.lower())
        if not mapper_class:
            raise ValueError(f"No status mapper found for courier: {courier}")
        return mapper_class()
    
    @classmethod
    def get_product_mapper(cls, courier: str) -> BaseProductMapper:
        """Get product mapper for specific courier."""
        mapper_class = cls.PRODUCT_MAPPERS.get(courier.lower())
        if not mapper_class:
            raise ValueError(f"No product mapper found for courier: {courier}")
        return mapper_class()
    
    @classmethod
    def get_response_mapper(cls, courier: str) -> BaseResponseMapper:
        """Get response mapper for specific courier."""
        mapper_class = cls.RESPONSE_MAPPERS.get(courier.lower())
        if not mapper_class:
            raise ValueError(f"No response mapper found for courier: {courier}")
        return mapper_class()
    
    @classmethod
    def get_payload_builder(cls, courier: str) -> BasePayloadBuilder:
        """Get payload builder for specific courier."""
        mapper_class = cls.PAYLOAD_BUILDERS.get(courier.lower())
        if not mapper_class:
            raise ValueError(f"No payload builder found for courier: {courier}")
        return mapper_class()
    
    @classmethod
    def get_supported_couriers(cls) -> list:
        """Get list of supported couriers."""
        return list(cls.STATUS_MAPPERS.keys())
    
    @classmethod
    def register_courier(cls, courier: str, status_mapper: Type[BaseStatusMapper] = None,
                        product_mapper: Type[BaseProductMapper] = None,
                        response_mapper: Type[BaseResponseMapper] = None,
                        payload_builder: Type[BasePayloadBuilder] = None):
        """Register a new courier's mapping services."""
        courier = courier.lower()
        
        if status_mapper:
            cls.STATUS_MAPPERS[courier] = status_mapper
        if product_mapper:
            cls.PRODUCT_MAPPERS[courier] = product_mapper
        if response_mapper:
            cls.RESPONSE_MAPPERS[courier] = response_mapper
        if payload_builder:
            cls.PAYLOAD_BUILDERS[courier] = payload_builder


# Global mapping factory instance
mapping_factory = MappingFactory()
