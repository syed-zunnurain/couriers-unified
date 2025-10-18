from django.db import transaction
from core.models import ShipmentType, Route
from ..models import Shipper, Consignee, ShipmentRequest


class ShipmentRequestService:
    """Service class for handling shipment request business logic."""
    
    @staticmethod
    def get_or_create_shipper(shipper_id=None, shipper_data=None):
        """Get existing shipper or create new one."""
        if shipper_id:
            return Shipper.objects.get(id=shipper_id)
        else:
            return Shipper.objects.get_or_create(
                email=shipper_data['email'],
                defaults=shipper_data
            )[0]
    
    @staticmethod
    def get_or_create_consignee(consignee_id=None, consignee_data=None):
        """Get existing consignee or create new one."""
        if consignee_id:
            return Consignee.objects.get(id=consignee_id)
        else:
            return Consignee.objects.get_or_create(
                email=consignee_data['email'],
                defaults=consignee_data
            )[0]
    
    @staticmethod
    def prepare_request_body(validated_data, shipper, consignee):
        """Prepare the JSON request body for storage."""
        return {
            'shipment_type_id': validated_data['shipment_type_id'],
            'shipper_id': shipper.id,
            'consignee_id': consignee.id,
            'pickup_date': validated_data['pickup_date'].isoformat() if hasattr(validated_data['pickup_date'], 'isoformat') else str(validated_data['pickup_date']),
            'weight': float(validated_data['weight']),
            'weight_unit': validated_data.get('weight_unit', 'kg'),
            'dimensions': validated_data['dimensions'],
            'dimension_unit': validated_data.get('dimension_unit', 'cm'),
            'special_instructions': validated_data.get('special_instructions', ''),
            'shipper_city': shipper.city,
            'consignee_city': consignee.city
        }
    
    @classmethod
    def check_existing_request(cls, reference_number):
        """Check if a shipment request with the same reference number already exists."""
        existing_request = ShipmentRequest.objects.filter(
            reference_number=reference_number
        ).order_by('-created_at').first()
        
        if existing_request:
            if existing_request.status in ['pending', 'processing']:
                return existing_request, 'already_processing'
            else:  # completed, cancelled
                return existing_request, 'can_create_new'
        
        return None, 'can_create_new'
    
    @classmethod
    def create_shipment_request(cls, validated_data):
        """Create a new shipment request with all related data."""
        reference_number = validated_data['reference_number']
        
        # Check if existing shipment was found in serializer
        if validated_data.get('action') == 'existing_shipment_found':
            existing_shipment = validated_data.get('existing_shipment')
            return {
                'action': 'existing_shipment_found',
                'shipment': existing_shipment,
                'message': 'Shipment with this reference number already exists',
                'status_code': 200,
                'data': {
                    'id': existing_shipment.id,
                    'reference_number': existing_shipment.reference_number,
                    'courier': existing_shipment.courier.name,
                    'tracking_number': existing_shipment.courier_external_id,
                    'status': 'completed',
                    'created_at': existing_shipment.created_at
                }
            }
        
        existing_request, status = cls.check_existing_request(reference_number)
        
        if status == 'already_processing':
            return {
                'action': 'already_exists',
                'shipment_request': existing_request,
                'shipper_id': existing_request.request_body.get('shipper_id'),
                'consignee_id': existing_request.request_body.get('consignee_id'),
                'message': 'Shipment request with this reference number is already under process',
                'status_code': 200,
                'data': {
                    'id': existing_request.id,
                    'reference_number': existing_request.reference_number,
                    'status': existing_request.status,
                    'created_at': existing_request.created_at,
                    'shipper_id': existing_request.request_body.get('shipper_id'),
                    'consignee_id': existing_request.request_body.get('consignee_id')
                }
            }
        
        with transaction.atomic():
            shipper = cls.get_or_create_shipper(
                shipper_id=validated_data.get('shipper_id'),
                shipper_data=validated_data.get('shipper')
            )
            
            consignee = cls.get_or_create_consignee(
                consignee_id=validated_data.get('consignee_id'),
                consignee_data=validated_data.get('consignee')
            )
            
            request_body = cls.prepare_request_body(validated_data, shipper, consignee)
            
            shipment_request = ShipmentRequest.objects.create(
                reference_number=validated_data['reference_number'],
                request_body=request_body,
                status='pending'
            )
            
            return {
                'action': 'created',
                'shipment_request': shipment_request,
                'shipper': shipper,
                'consignee': consignee,
                'message': 'Shipment request created successfully',
                'status_code': 201,
                'data': {
                    'id': shipment_request.id,
                    'reference_number': shipment_request.reference_number,
                    'status': shipment_request.status,
                    'created_at': shipment_request.created_at,
                    'shipper_id': shipper.id,
                    'consignee_id': consignee.id
                }
            }
