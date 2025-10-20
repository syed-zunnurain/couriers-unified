import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..services.cancellation import ShipmentCancellationService

logger = logging.getLogger(__name__)


@api_view(['POST'])
def cancel_shipment(request, reference_number: str):
    """
    Cancel shipment by reference number.
    
    Args:
        reference_number: The shipment reference number (path parameter)
        
    Returns:
        JSON response with cancellation result or error
    """
    try:
        logger.info(f"Cancel Shipment: Received cancellation request for {reference_number}")
        
        cancellation_service = ShipmentCancellationService()
        result = cancellation_service.cancel_shipment_by_reference(reference_number)
        
        if result['success']:
            logger.info(f"Cancel Shipment: Successfully cancelled shipment {reference_number}")
            return Response(
                {
                    'success': True,
                    'message': result['message'],
                    'data': {
                        'shipment_id': result.get('shipment_id'),
                        'reference_number': result.get('reference_number')
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            logger.warning(f"Cancel Shipment: Failed to cancel shipment {reference_number}: {result.get('message')}")
            return Response(
                {
                    'success': False,
                    'message': result.get('message'),
                    'error_code': result.get('error_code')
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Cancel Shipment: Unexpected error cancelling {reference_number}: {str(e)}")
        return Response(
            {
                'success': False,
                'message': 'Internal server error',
                'error_code': 'INTERNAL_ERROR'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
