import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DHLStatusMapper:
    DHL_STATUS_MAPPING = {
        'OK': 'completed',
        'SUCCESS': 'completed',
        'PROCESSED': 'completed',
        'IN_TRANSIT': 'in_transit',
        'DELIVERED': 'delivered',
        'PENDING': 'pending',
        'FAILED': 'failed',
        'CANCELLED': 'cancelled',
        'ERROR': 'failed'
    }
    
    @classmethod
    def map_dhl_status(cls, dhl_status: str) -> str:
        return cls.DHL_STATUS_MAPPING.get(dhl_status.upper(), 'unknown')
    
    @classmethod
    def get_supported_statuses(cls) -> list:
        return list(cls.DHL_STATUS_MAPPING.keys())
