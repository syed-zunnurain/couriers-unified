import logging
from django.db import transaction
from ...repositories.repository_factory import repositories
from ...schemas.shipment_request_response import ShipmentRequestResponse

logger = logging.getLogger(__name__)


class ShipmentRequestService:
    @staticmethod
    def get_or_create_shipper(shipper_id=None, shipper_data=None):
        if shipper_id:
            return repositories.shipper.get_by_id(shipper_id)
        else:
            return repositories.shipper.get_or_create_by_email(
                shipper_data['email'],
                defaults=shipper_data
            )[0]
    
    @staticmethod
    def get_or_create_consignee(consignee_id=None, consignee_data=None):
        if consignee_id:
            return repositories.consignee.get_by_id(consignee_id)
        else:
            return repositories.consignee.get_or_create_by_email(
                consignee_data['email'],
                defaults=consignee_data
            )[0]
    
    @staticmethod
    def prepare_request_body(validated_data, shipper, consignee):
        pickup_date = validated_data.get('pickup_date')
        if pickup_date:
            pickup_date_str = pickup_date.isoformat() if hasattr(pickup_date, 'isoformat') else str(pickup_date)
        else:
            pickup_date_str = None
            
        return {
            'shipment_type_id': validated_data['shipment_type_id'],
            'shipper_id': shipper.id,
            'consignee_id': consignee.id,
            'pickup_date': pickup_date_str,
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
        existing_request = repositories.shipment_request.get_latest_by_reference_number(reference_number)
        
        if existing_request:
            if existing_request.status in ['pending', 'processing']:
                return existing_request, 'already_processing'
            else:  # completed, cancelled
                return existing_request, 'can_create_new'
        
        return None, 'can_create_new'
    
    @classmethod
    def create_shipment_request(cls, validated_data):
        reference_number = validated_data['reference_number']
        
        if validated_data.get('action') == 'existing_shipment_found':
            existing_shipment = validated_data.get('existing_shipment')
            return ShipmentRequestResponse.create_response('existing_shipment', existing_shipment=existing_shipment)
        
        existing_request, status = cls.check_existing_request(reference_number)
        
        if status == 'already_processing':
            return ShipmentRequestResponse.create_response('already_processing', shipment_request=existing_request)
        
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
            logger.info(f"ShipmentRequestService: Creating shipment request with body: {request_body}")
            
            shipment_request = repositories.shipment_request.create(
                reference_number=validated_data['reference_number'],
                request_body=request_body,
                status='pending'
            )
            
            return ShipmentRequestResponse.create_response(
                'new',
                shipment_request=shipment_request,
                shipper_id=shipper.id,
                consignee_id=consignee.id
            )
