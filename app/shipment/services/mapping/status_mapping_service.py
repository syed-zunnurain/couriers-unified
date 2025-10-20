import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class StatusMappingService:
    """Service for mapping courier-specific statuses to standardized statuses."""
    
    # Standardized status mappings
    STANDARD_STATUSES = {
        'created': 'created',
        'picked_up': 'picked_up',
        'in_transit': 'in_transit',
        'out_for_delivery': 'out_for_delivery',
        'delivered': 'delivered',
        'exception': 'exception',
        'cancelled': 'cancelled',
        'returned': 'returned',
        'pending': 'pending',
        'processing': 'processing',
        'failed': 'failed'
    }
    
    # DHL-specific status mappings
    DHL_STATUS_MAPPING = {
        'OK': 'delivered',
        'SUCCESS': 'delivered',
        'PROCESSED': 'delivered',
        'IN_TRANSIT': 'in_transit',
        'DELIVERED': 'delivered',
        'PENDING': 'pending',
        'FAILED': 'failed',
        'CANCELLED': 'cancelled',
        'ERROR': 'exception',
        'EXCEPTION': 'exception',
        'RETURNED': 'returned',
        'OUT_FOR_DELIVERY': 'out_for_delivery',
        'PICKED_UP': 'picked_up'
    }
    
    # FedEx-specific status mappings (for future use)
    FEDEX_STATUS_MAPPING = {
        'PICKED_UP': 'picked_up',
        'IN_TRANSIT': 'in_transit',
        'OUT_FOR_DELIVERY': 'out_for_delivery',
        'DELIVERED': 'delivered',
        'EXCEPTION': 'exception',
        'CANCELLED': 'cancelled',
        'RETURNED': 'returned'
    }
    
    # UPS-specific status mappings (for future use)
    UPS_STATUS_MAPPING = {
        'PICKED_UP': 'picked_up',
        'IN_TRANSIT': 'in_transit',
        'OUT_FOR_DELIVERY': 'out_for_delivery',
        'DELIVERED': 'delivered',
        'EXCEPTION': 'exception',
        'CANCELLED': 'cancelled',
        'RETURNED': 'returned'
    }
    
    @classmethod
    def get_courier_mapping(cls, courier_name: str) -> Dict[str, str]:
        """Get status mapping for a specific courier."""
        courier_mappings = {
            'dhl': cls.DHL_STATUS_MAPPING,
            'fedex': cls.FEDEX_STATUS_MAPPING,
            'ups': cls.UPS_STATUS_MAPPING
        }
        return courier_mappings.get(courier_name.lower(), {})
    
    @classmethod
    def map_courier_status(cls, courier_name: str, courier_status: str) -> str:
        """Map courier-specific status to standardized status."""
        mapping = cls.get_courier_mapping(courier_name)
        standardized_status = mapping.get(courier_status.upper(), 'unknown')
        
        logger.debug(f"StatusMappingService: Mapped '{courier_status}' from {courier_name} to '{standardized_status}'")
        return standardized_status
    
    @classmethod
    def get_standard_statuses(cls) -> List[str]:
        """Get list of all standardized statuses."""
        return list(cls.STANDARD_STATUSES.keys())
    
    @classmethod
    def get_courier_statuses(cls, courier_name: str) -> List[str]:
        """Get list of statuses supported by a specific courier."""
        mapping = cls.get_courier_mapping(courier_name)
        return list(mapping.keys())
    
    @classmethod
    def is_valid_status(cls, status: str) -> bool:
        """Check if a status is valid."""
        return status.lower() in cls.STANDARD_STATUSES
    
    @classmethod
    def get_status_display_name(cls, status: str) -> str:
        """Get display name for a status."""
        display_names = {
            'created': 'Created',
            'picked_up': 'Picked Up',
            'in_transit': 'In Transit',
            'out_for_delivery': 'Out for Delivery',
            'delivered': 'Delivered',
            'exception': 'Exception',
            'cancelled': 'Cancelled',
            'returned': 'Returned',
            'pending': 'Pending',
            'processing': 'Processing',
            'failed': 'Failed'
        }
        return display_names.get(status.lower(), status.title())
