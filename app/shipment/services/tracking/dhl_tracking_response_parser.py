import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DHLTrackingResponseParser:
    @staticmethod
    def parse_tracking_response(response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            if 'shipments' in response_data and response_data['shipments']:
                shipment = response_data['shipments'][0]
                return {
                    'success': True,
                    'tracking_number': shipment.get('id', ''),
                    'service': shipment.get('service', ''),
                    'current_status': shipment.get('status', {}).get('status', 'UNKNOWN'),
                    'status_description': shipment.get('status', {}).get('description', ''),
                    'current_location': DHLTrackingResponseParser._parse_location(shipment.get('status', {}).get('location', {})),
                    'events': DHLTrackingResponseParser._parse_events(shipment.get('events', [])),
                    'origin': DHLTrackingResponseParser._parse_location(shipment.get('origin', {})),
                    'destination': DHLTrackingResponseParser._parse_location(shipment.get('destination', {})),
                    'details': DHLTrackingResponseParser._parse_details(shipment.get('details', {}))
                }
            
            return None
            
        except Exception as e:
            logger.error(f"DHLTrackingResponseParser: Error parsing tracking response: {str(e)}")
            return None
    
    @staticmethod
    def _parse_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        
        Args:
            events: List of events from DHL API
            
        Returns:
            List of parsed events
        """
        parsed_events = []
        
        for event in events:
            try:
                parsed_event = {
                    'timestamp': event.get('timestamp', ''),
                    'status': event.get('status', 'UNKNOWN'),
                    'description': event.get('description', ''),
                    'location': DHLTrackingResponseParser._parse_location(event.get('location', {}))
                }
                parsed_events.append(parsed_event)
            except Exception as e:
                logger.error(f"DHLTrackingResponseParser: Error parsing event: {str(e)}")
                continue
        
        return parsed_events
    
    @staticmethod
    def _parse_location(location: Dict[str, Any]) -> Dict[str, str]:
        """
        Parse location information from DHL response.
        
        Args:
            location: Location data from DHL API
            
        Returns:
            Dict containing location information
        """
        address = location.get('address', {})
        return {
            'address': address.get('addressLocality', ''),
            'city': address.get('addressLocality', ''),
            'country': address.get('countryCode', ''),
            'postal_code': address.get('postalCode', '')
        }
    
    @staticmethod
    def _parse_details(details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse shipment details from DHL response.
        
        Args:
            details: Details data from DHL API
            
        Returns:
            Dict containing parsed details
        """
        try:
            product = details.get('product', {})
            weight = details.get('weight', {})
            references = details.get('references', [])
            
            parsed_references = []
            for ref in references:
                parsed_references.append({
                    'number': ref.get('number', ''),
                    'type': ref.get('type', '')
                })
            
            return {
                'product_name': product.get('productName', ''),
                'weight': {
                    'value': weight.get('value', 0),
                    'unit': weight.get('unitText', '')
                },
                'references': parsed_references
            }
        except Exception as e:
            logger.error(f"DHLTrackingResponseParser: Error parsing details: {str(e)}")
            return {}
    
    @staticmethod
    def parse_error_response(error_message: str) -> Dict[str, Any]:
        """
        Parse DHL tracking error messages to return clean error messages and codes.
        """
        error_code = 'COURIER_API_ERROR'
        clean_error_message = 'Failed to track shipment with courier'

        if 'HTTP 400' in error_message:
            error_code = 'COURIER_BAD_REQUEST'
            clean_error_message = 'Invalid tracking request to courier'
        elif 'HTTP 401' in error_message:
            error_code = 'COURIER_UNAUTHORIZED'
            clean_error_message = 'Authentication failed with courier'
        elif 'HTTP 403' in error_message:
            error_code = 'COURIER_FORBIDDEN'
            clean_error_message = 'Access denied by courier'
        elif 'HTTP 404' in error_message:
            error_code = 'SHIPMENT_NOT_FOUND_IN_COURIER'
            clean_error_message = 'Shipment not found in courier system'
        elif 'HTTP 500' in error_message:
            error_code = 'COURIER_SERVER_ERROR'
            clean_error_message = 'Courier service temporarily unavailable'
        
        return {
            'error_message': clean_error_message,
            'error_code': error_code
        }
