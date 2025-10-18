from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ShipmentRequestCreateSerializer
from .services import ShipmentRequestService


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