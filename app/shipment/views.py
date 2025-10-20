from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ShipmentRequestCreateSerializer
from .services import ShipmentRequestService
from .services.shipment_label_service import ShipmentLabelService


@api_view(['POST'])
def create_shipment_request(request):
    
    serializer = ShipmentRequestCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = ShipmentRequestService.create_shipment_request(serializer.validated_data)
        
        return Response(
            {
                'success': True,
                'message': result['message'],
                'data': result['data']
            },
            status=result['status_code']
        )
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Failed to create shipment request',
                'error': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_shipment_label(request, reference_number: str):
    """
    Get shipment label by reference number.
    
    Args:
        reference_number: The shipment reference number (path parameter)
        
    Returns:
        JSON response with label information or error
    """
    try:
        from .services.label_response_handler import LabelResponseHandler
        
        label_service = ShipmentLabelService()
        result = label_service.get_shipment_label_by_reference(reference_number)
        
        return LabelResponseHandler.handle_result(result)
            
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )