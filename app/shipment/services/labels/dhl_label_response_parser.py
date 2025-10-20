"""DHL label response parser for handling label-specific responses."""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DHLLabelResponseParser:
    """Parser for DHL label API responses."""
    
    @staticmethod
    def parse_success_response(response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse successful DHL label response.
        
        Args:
            response_data: The response data from DHL API
            
        Returns:
            Dict containing label data or None if parsing fails
        """
        try:
            if 'items' in response_data and response_data['items']:
                items = response_data['items']
                if len(items) > 0 and 'label' in items[0]:
                    label_data = items[0]['label']
                    if 'url' in label_data:
                        return {
                            'success': True,
                            'url': label_data['url'],
                            'format': label_data.get('fileFormat', 'PDF')
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"DHLLabelResponseParser: Error parsing success response: {str(e)}")
            return None
    
    @staticmethod
    def parse_error_response(error_message: str) -> Dict[str, Any]:
        """
        Parse DHL error response and return clean error message.
        
        Args:
            error_message: The error message from DHL API
            
        Returns:
            Dict containing error_code and clean error_message
        """
        try:
            error_code = 'COURIER_API_ERROR'
            clean_message = 'Failed to fetch label from DHL'
            
            if 'HTTP 400' in error_message:
                return DHLLabelResponseParser._parse_400_error(error_message)
            elif 'HTTP 401' in error_message:
                error_code = 'COURIER_UNAUTHORIZED'
                clean_message = 'Authentication failed with courier'
            elif 'HTTP 403' in error_message:
                error_code = 'COURIER_FORBIDDEN'
                clean_message = 'Access denied by courier'
            elif 'HTTP 404' in error_message:
                error_code = 'COURIER_NOT_FOUND'
                clean_message = 'Courier service not found'
            elif 'HTTP 500' in error_message:
                error_code = 'COURIER_SERVER_ERROR'
                clean_message = 'Courier service temporarily unavailable'
            
            return {
                'error_code': error_code,
                'error_message': clean_message
            }
            
        except Exception as e:
            logger.error(f"DHLLabelResponseParser: Error parsing error response: {str(e)}")
            return {
                'error_code': 'COURIER_API_ERROR',
                'error_message': 'Failed to fetch label from DHL'
            }
    
    @staticmethod
    def _parse_400_error(error_message: str) -> Dict[str, Any]:
        """
        Parse HTTP 400 error response from DHL.
        
        Args:
            error_message: The error message containing JSON
            
        Returns:
            Dict containing error_code and clean error_message
        """
        try:
            json_start = error_message.find('{')
            if json_start == -1:
                return {
                    'error_code': 'COURIER_BAD_REQUEST',
                    'error_message': 'Invalid request to courier'
                }
            
            json_str = error_message[json_start:]
            dhl_error = json.loads(json_str)
            
            if 'items' in dhl_error and dhl_error['items']:
                item = dhl_error['items'][0]
                if 'sstatus' in item and 'UNKNOWN_SHIPMENT_NUMBER' in str(item['sstatus']):
                    return {
                        'error_code': 'SHIPMENT_NOT_FOUND_IN_COURIER',
                        'error_message': f"Shipment {item.get('shipmentNo', '')} not found in courier system"
                    }
                else:
                    return {
                        'error_code': 'COURIER_BAD_REQUEST',
                        'error_message': dhl_error.get('status', {}).get('detail', 'Invalid request to courier')
                    }
            else:
                return {
                    'error_code': 'COURIER_BAD_REQUEST',
                    'error_message': dhl_error.get('status', {}).get('detail', 'Invalid request to courier')
                }
                
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"DHLLabelResponseParser: Error parsing 400 error: {str(e)}")
            return {
                'error_code': 'COURIER_BAD_REQUEST',
                'error_message': 'Invalid request to courier'
            }
