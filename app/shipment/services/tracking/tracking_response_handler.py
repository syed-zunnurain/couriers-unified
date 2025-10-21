import logging
from rest_framework.response import Response
from rest_framework import status
from typing import Dict, Any
from ...schemas.tracking_response import TrackingResponse

logger = logging.getLogger(__name__)


class TrackingResponseHandler:
    @staticmethod
    def handle_result(result: TrackingResponse) -> Response:
        if result.success:
            data = result.to_dict()
            data.pop('success', None)
            return Response(
                {
                    'success': True,
                    'message': 'Tracking information retrieved successfully',
                    'data': data
                },
                status=status.HTTP_200_OK
            )
        else:
            error_code = result.error_code or 'UNKNOWN_ERROR'
            http_status = TrackingResponseHandler._map_error_code_to_http_status(error_code)

            return Response(
                {
                    'success': False,
                    'message': 'Failed to retrieve tracking information',
                    'error': result.error,
                    'error_code': error_code
                },
                status=http_status
            )

    @staticmethod
    def _map_error_code_to_http_status(error_code: str) -> int:
        if error_code in ['SHIPMENT_NOT_FOUND', 'SHIPMENT_NOT_FOUND_IN_COURIER', 'COURIER_NOT_FOUND']:
            return status.HTTP_404_NOT_FOUND
        elif error_code in ['UNSUPPORTED_COURIER', 'COURIER_BAD_REQUEST']:
            return status.HTTP_400_BAD_REQUEST
        elif error_code == 'COURIER_UNAUTHORIZED':
            return status.HTTP_401_UNAUTHORIZED
        elif error_code == 'COURIER_FORBIDDEN':
            return status.HTTP_403_FORBIDDEN
        elif error_code in ['COURIER_API_ERROR', 'TRACKING_DATA_NOT_FOUND', 'COURIER_SERVER_ERROR']:
            return status.HTTP_502_BAD_GATEWAY
        elif error_code == 'INTERNAL_ERROR':
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
