"""Response handler for shipment label operations."""

from rest_framework import status
from rest_framework.response import Response
from typing import Dict, Any


class LabelResponseHandler:
    """Handles HTTP responses for label operations."""
    
    @staticmethod
    def success_response(label_data: Dict[str, Any]) -> Response:
        """
        Create success response for label retrieval.
        
        Args:
            label_data: The label data to return
            
        Returns:
            DRF Response with success data
        """
        return Response(
            {
                'success': True,
                'message': 'Label retrieved successfully',
                'data': label_data
            },
            status=status.HTTP_200_OK
        )
    
    @staticmethod
    def error_response(result: Dict[str, Any]) -> Response:
        """
        Create error response based on error code.
        
        Args:
            result: The result dict containing error information
            
        Returns:
            DRF Response with appropriate error status
        """
        error_code = result.get('error_code', 'UNKNOWN_ERROR')
        error_message = result.get('error', 'Unknown error occurred')
        
        # Map error codes to HTTP status codes
        status_mapping = {
            'SHIPMENT_NOT_FOUND': status.HTTP_404_NOT_FOUND,
            'SHIPMENT_NOT_FOUND_IN_COURIER': status.HTTP_404_NOT_FOUND,
            'UNSUPPORTED_COURIER': status.HTTP_400_BAD_REQUEST,
            'COURIER_BAD_REQUEST': status.HTTP_400_BAD_REQUEST,
            'COURIER_UNAUTHORIZED': status.HTTP_401_UNAUTHORIZED,
            'COURIER_FORBIDDEN': status.HTTP_403_FORBIDDEN,
            'COURIER_NOT_FOUND': status.HTTP_404_NOT_FOUND,
            'COURIER_API_ERROR': status.HTTP_502_BAD_GATEWAY,
            'LABEL_URL_NOT_FOUND': status.HTTP_502_BAD_GATEWAY,
            'COURIER_SERVER_ERROR': status.HTTP_502_BAD_GATEWAY,
            'DATABASE_ERROR': status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        
        http_status = status_mapping.get(error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(
            {
                'success': False,
                'message': 'Failed to retrieve label',
                'error': error_message,
                'error_code': error_code
            },
            status=http_status
        )
    
    @staticmethod
    def handle_result(result: Dict[str, Any]) -> Response:
        """
        Handle service result and return appropriate response.
        
        Args:
            result: The result from the service
            
        Returns:
            DRF Response
        """
        if result.get('success'):
            return LabelResponseHandler.success_response(result.get('label'))
        else:
            return LabelResponseHandler.error_response(result)
