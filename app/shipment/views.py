from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ShipmentRequestCreateSerializer
from .services import ShipmentRequestService
from .services.labels.shipment_label_service import ShipmentLabelService
from .services.tracking.shipment_tracking_service import ShipmentTrackingService
from .services.cancellation import ShipmentCancellationService


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
            result.to_dict(),
            status=result.status_code
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
    try:
        from .services.labels.label_response_handler import LabelResponseHandler
        
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


@api_view(['GET'])
def track_shipment(request, reference_number: str):
    try:
        from .services.tracking.tracking_response_handler import TrackingResponseHandler
        
        tracking_service = ShipmentTrackingService()
        result = tracking_service.track_shipment_by_reference(reference_number)
        
        return TrackingResponseHandler.handle_result(result)
            
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def cancel_shipment(request, reference_number: str):
    try:
        cancellation_service = ShipmentCancellationService()
        result = cancellation_service.cancel_shipment_by_reference(reference_number)
        
        if result.success:
            return Response(
                result.to_dict(),
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                result.to_dict(),
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': 'Internal server error',
                'error_code': 'INTERNAL_ERROR'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )