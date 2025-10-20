"""DHL webhook validator following Single Responsibility Principle."""

import logging
from typing import Dict, Any, Optional
from django.http import HttpRequest

logger = logging.getLogger(__name__)


class DHLWebhookValidator:
    """
    Single Responsibility: Validate DHL webhook requests and payloads.
    
    This class only handles validation of webhook requests.
    It doesn't parse, process, or store data - just validates.
    """
    
    @classmethod
    def validate_request(cls, request: HttpRequest) -> bool:
        """
        Validate the incoming webhook request.
        
        Args:
            request: Django HTTP request object
            
        Returns:
            True if request is valid, False otherwise
        """
        try:
            logger.info("DHLWebhookValidator: Starting request validation")
            
            # Check HTTP method
            if not cls._validate_http_method(request):
                logger.warning("DHLWebhookValidator: Invalid HTTP method")
                return False
            
            # Check content type
            if not cls._validate_content_type(request):
                logger.warning("DHLWebhookValidator: Invalid content type")
                return False
            
            # Check headers
            if not cls._validate_headers(request):
                logger.warning("DHLWebhookValidator: Invalid headers")
                return False
            
            logger.info("DHLWebhookValidator: Request validation successful")
            return True
            
        except Exception as e:
            logger.error(f"DHLWebhookValidator: Error validating request: {str(e)}")
            return False
    
    @classmethod
    def validate_payload(cls, payload: Dict[str, Any]) -> bool:
        """
        Validate the webhook payload structure and content.
        
        Args:
            payload: Parsed JSON payload from webhook
            
        Returns:
            True if payload is valid, False otherwise
        """
        try:
            logger.info("DHLWebhookValidator: Starting payload validation")
            
            # Check if payload is not empty
            if not payload:
                logger.warning("DHLWebhookValidator: Empty payload")
                return False
            
            # Check required fields
            if not cls._validate_required_fields(payload):
                logger.warning("DHLWebhookValidator: Missing required fields")
                return False
            
            # Check data types
            if not cls._validate_data_types(payload):
                logger.warning("DHLWebhookValidator: Invalid data types")
                return False
            
            logger.info("DHLWebhookValidator: Payload validation successful")
            return True
            
        except Exception as e:
            logger.error(f"DHLWebhookValidator: Error validating payload: {str(e)}")
            return False
    
    @classmethod
    def _validate_http_method(cls, request: HttpRequest) -> bool:
        """Validate HTTP method is POST."""
        return request.method == 'POST'
    
    @classmethod
    def _validate_content_type(cls, request: HttpRequest) -> bool:
        """Validate content type is JSON."""
        content_type = request.content_type
        return content_type and 'application/json' in content_type.lower()
    
    @classmethod
    def _validate_headers(cls, request: HttpRequest) -> bool:
        """Validate required headers including API key."""
        from django.conf import settings
        
        # Check content type
        if 'content-type' not in request.headers:
            logger.warning("DHLWebhookValidator: Missing content-type header")
            return False
        
        # Check API key
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
        expected_key = getattr(settings, 'DHL_WEBHOOK_API_KEY', None)
        
        if not api_key or not expected_key or api_key != expected_key:
            logger.warning("DHLWebhookValidator: Invalid or missing API key")
            return False
        
        return True
    
    @classmethod
    def _validate_required_fields(cls, payload: Dict[str, Any]) -> bool:
        """Validate that required fields are present in payload."""
        # At minimum, we need some form of tracking identifier and status
        has_tracking_id = cls._has_tracking_identifier(payload)
        has_status = cls._has_status_information(payload)
        
        if not has_tracking_id:
            logger.warning("DHLWebhookValidator: No tracking identifier found")
            return False
        
        if not has_status:
            logger.warning("DHLWebhookValidator: No status information found")
            return False
        
        return True
    
    @classmethod
    def _has_tracking_identifier(cls, payload: Dict[str, Any]) -> bool:
        """Check if payload contains a tracking identifier."""
        # Based on actual DHL webhook format
        if 'tracking_number' in payload and payload['tracking_number']:
            return True
        
        # Fallback to other possible fields
        tracking_fields = [
            'trackingNumber',
            'shipmentId',
            'shipment_id',
            'id',
            'trackingId',
            'tracking_id'
        ]
        
        # Check direct fields
        for field in tracking_fields:
            if field in payload and payload[field]:
                return True
        
        return False
    
    @classmethod
    def _has_status_information(cls, payload: Dict[str, Any]) -> bool:
        """Check if payload contains status information."""
        # Based on actual DHL webhook format
        if 'status' in payload and payload['status']:
            return True
        
        # Fallback to other possible fields
        status_fields = [
            'statusCode',
            'status_code',
            'eventType',
            'event_type',
            'state',
            'currentStatus',
            'current_status'
        ]
        
        # Check direct fields
        for field in status_fields:
            if field in payload and payload[field]:
                return True
        
        return False
    
    @classmethod
    def _validate_data_types(cls, payload: Dict[str, Any]) -> bool:
        """Validate data types of payload fields."""
        try:
            # Ensure payload is a dictionary
            if not isinstance(payload, dict):
                logger.warning("DHLWebhookValidator: Payload is not a dictionary")
                return False
            
            # Check that string fields are actually strings
            string_fields = ['trackingNumber', 'status', 'timestamp']
            for field in string_fields:
                if field in payload and payload[field] is not None:
                    if not isinstance(payload[field], str):
                        logger.warning(f"DHLWebhookValidator: Field '{field}' is not a string")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"DHLWebhookValidator: Error validating data types: {str(e)}")
            return False
