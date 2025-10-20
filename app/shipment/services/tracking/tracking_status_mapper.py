"""Service for mapping courier tracking statuses to standardized statuses."""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class TrackingStatusMapper:
    """Maps courier-specific tracking statuses to standardized statuses."""
    
    STANDARD_STATUSES = {
        'CREATED': 'Shipment created',
        'PICKED_UP': 'Package picked up',
        'IN_TRANSIT': 'Package in transit',
        'OUT_FOR_DELIVERY': 'Out for delivery',
        'DELIVERED': 'Package delivered',
        'EXCEPTION': 'Delivery exception',
        'RETURNED': 'Package returned',
        'CANCELLED': 'Shipment cancelled',
        'UNKNOWN': 'Status unknown'
    }
    
    DHL_STATUS_MAPPING = {
        'CREATED': 'CREATED',
        'PICKED_UP': 'PICKED_UP',
        'IN_TRANSIT': 'IN_TRANSIT',
        'OUT_FOR_DELIVERY': 'OUT_FOR_DELIVERY',
        'DELIVERED': 'DELIVERED',
        'EXCEPTION': 'EXCEPTION',
        'RETURNED': 'RETURNED',
        'CANCELLED': 'CANCELLED',
        'UNKNOWN': 'UNKNOWN'
    }
    
    @classmethod
    def map_courier_status(cls, courier_name: str, courier_status: str) -> Dict[str, str]:
        """
        Map courier-specific status to standardized status.
        
        Args:
            courier_name: Name of the courier (e.g., 'dhl')
            courier_status: Status from courier API
            
        Returns:
            Dict containing standardized status and description
        """
        try:
            courier_name_lower = courier_name.lower()
            
            if courier_name_lower == 'dhl':
                return cls._map_dhl_status(courier_status)
            else:
                return {
                    'status': 'UNKNOWN',
                    'description': f'Unknown status from {courier_name}: {courier_status}'
                }
                
        except Exception as e:
            logger.error(f"TrackingStatusMapper: Error mapping status: {str(e)}")
            return {
                'status': 'UNKNOWN',
                'description': f'Error mapping status: {str(e)}'
            }
    
    @classmethod
    def _map_dhl_status(cls, dhl_status: str) -> Dict[str, str]:
        """
        Map DHL-specific status to standardized status.
        
        Args:
            dhl_status: Status from DHL API
            
        Returns:
            Dict containing standardized status and description
        """
        dhl_status_upper = dhl_status.upper()
        
        if 'LABEL CREATED' in dhl_status_upper:
            mapped_status = 'CREATED'
        elif 'PACKAGE RECEIVED' in dhl_status_upper or 'PROCESSED' in dhl_status_upper:
            mapped_status = 'PICKED_UP'
        elif 'DEPARTURE' in dhl_status_upper or 'ARRIVAL' in dhl_status_upper or 'TENDERED' in dhl_status_upper:
            mapped_status = 'IN_TRANSIT'
        elif 'OUT FOR DELIVERY' in dhl_status_upper:
            mapped_status = 'OUT_FOR_DELIVERY'
        elif 'DELIVERED' in dhl_status_upper:
            mapped_status = 'DELIVERED'
        elif 'EXCEPTION' in dhl_status_upper or 'PROBLEM' in dhl_status_upper:
            mapped_status = 'EXCEPTION'
        elif 'RETURN' in dhl_status_upper:
            mapped_status = 'RETURNED'
        elif 'CANCELLED' in dhl_status_upper or 'CANCEL' in dhl_status_upper:
            mapped_status = 'CANCELLED'
        elif 'EN ROUTE' in dhl_status_upper or 'AWAITING' in dhl_status_upper:
            mapped_status = 'CREATED'
        else:
            mapped_status = 'UNKNOWN'
        
        return {
            'status': mapped_status,
            'description': cls.STANDARD_STATUSES.get(mapped_status, f'Unknown status: {mapped_status}')
        }
    
    @classmethod
    def get_standard_statuses(cls) -> Dict[str, str]:
        """
        Get all standardized tracking statuses.
        
        Returns:
            Dict of status codes to descriptions
        """
        return cls.STANDARD_STATUSES.copy()
