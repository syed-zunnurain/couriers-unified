import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .services.webhooks import (
    DHLWebhookParser,
    DHLWebhookValidator,
    DHLWebhookProcessor
)

logger = logging.getLogger(__name__)


@api_view(['POST'])
@csrf_exempt
def dhl_webhook(request):
    try:
        logger.info("DHL Webhook: Received webhook request")
        
        if not DHLWebhookValidator.validate_request(request):
            logger.warning("DHL Webhook: Request validation failed")
            return Response(
                {
                    'success': False,
                    'message': 'Invalid request or API key',
                    'error_code': 'INVALID_REQUEST'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"DHL Webhook: JSON decode error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'message': 'Invalid JSON payload',
                    'error_code': 'INVALID_JSON'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Step 3: Validate the payload
        if not DHLWebhookValidator.validate_payload(payload):
            logger.warning("DHL Webhook: Payload validation failed")
            return Response(
                {
                    'success': False,
                    'message': 'Invalid payload structure',
                    'error_code': 'INVALID_PAYLOAD'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Step 4: Parse webhook data
        webhook_data = DHLWebhookParser.parse(payload)
        if not webhook_data:
            logger.warning("DHL Webhook: Failed to parse webhook data")
            return Response(
                {
                    'success': False,
                    'message': 'Failed to parse webhook data',
                    'error_code': 'PARSE_ERROR'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Step 5: Process the webhook
        processor = DHLWebhookProcessor()
        result = processor.process_webhook(webhook_data)
        
        if result['success']:
            logger.info(f"DHL Webhook: Successfully processed webhook for shipment {result.get('reference_number')}")
            
            # Check if it's a duplicate or cancelled
            if result.get('status') == 'duplicate_ignored':
                return Response(
                    {
                        'success': True,
                        'message': 'Duplicate status ignored',
                        'data': {
                            'shipment_id': result.get('shipment_id'),
                            'reference_number': result.get('reference_number'),
                            'status_entry_id': result.get('status_entry_id'),
                            'mapped_status': result.get('mapped_status'),
                            'status': 'duplicate_ignored'
                        }
                    },
                    status=status.HTTP_200_OK
                )
            elif result.get('status') == 'cancelled_ignored':
                return Response(
                    {
                        'success': True,
                        'message': 'Shipment already cancelled, webhook ignored',
                        'data': {
                            'shipment_id': result.get('shipment_id'),
                            'reference_number': result.get('reference_number'),
                            'status_entry_id': result.get('status_entry_id'),
                            'mapped_status': result.get('mapped_status'),
                            'status': 'cancelled_ignored'
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'success': True,
                        'message': 'Webhook processed successfully',
                        'data': {
                            'shipment_id': result.get('shipment_id'),
                            'reference_number': result.get('reference_number'),
                            'status_entry_id': result.get('status_entry_id'),
                            'mapped_status': result.get('mapped_status')
                        }
                    },
                    status=status.HTTP_200_OK
                )
        else:
            logger.warning(f"DHL Webhook: Processing failed: {result.get('message')}")
            return Response(
                {
                    'success': False,
                    'message': result.get('message'),
                    'error_code': result.get('error_code')
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"DHL Webhook: Unexpected error: {str(e)}")
        return Response(
            {
                'success': False,
                'message': 'Internal server error',
                'error_code': 'INTERNAL_ERROR'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


