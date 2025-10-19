from rest_framework import serializers
from core.models import ShipmentType, Route
from .models import Shipper, Consignee, ShipmentRequest
from .repositories.repository_factory import repositories


class ShipperSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating shippers."""
    
    class Meta:
        model = Shipper
        fields = ['name', 'address', 'postal_code', 'city', 'country', 'phone', 'email']
        extra_kwargs = {
            'postal_code': {'required': False, 'allow_blank': True}
        }


class ConsigneeSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating consignees."""
    
    class Meta:
        model = Consignee
        fields = ['name', 'address', 'postal_code', 'city', 'country', 'phone', 'email']
        extra_kwargs = {
            'postal_code': {'required': False, 'allow_blank': True}
        }


class ShipmentRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating shipment requests."""
    
    # Required fields
    shipment_type_id = serializers.IntegerField()
    reference_number = serializers.CharField(max_length=255)
    
    # Shipper - either ID or full information
    shipper_id = serializers.IntegerField(required=False, allow_null=True)
    shipper = ShipperSerializer(required=False)
    
    # Consignee - either ID or full information
    consignee_id = serializers.IntegerField(required=False, allow_null=True)
    consignee = ConsigneeSerializer(required=False)
    
    # Shipment details
    items = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of items in the shipment"
    )
    pickup_date = serializers.DateField(required=False, allow_null=True)
    weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    weight_unit = serializers.CharField(
        max_length=10,
        default='kg',
        help_text="Unit of measurement for weight (e.g., kg, lb, g)"
    )
    dimensions = serializers.DictField(
        help_text="Dimensions in format: {length: 10, width: 5, height: 3}"
    )
    dimension_unit = serializers.CharField(
        max_length=10,
        default='cm',
        help_text="Unit of measurement for dimensions (e.g., cm, in, m)"
    )
    special_instructions = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Special instructions for the shipment"
    )
    
    def validate(self, data):
        """Validate that either shipper_id or shipper data is provided and cities match route."""
        if not data.get('shipper_id') and not data.get('shipper'):
            raise serializers.ValidationError(
                "Either 'shipper_id' or 'shipper' information must be provided."
            )
        
        if not data.get('consignee_id') and not data.get('consignee'):
            raise serializers.ValidationError(
                "Either 'consignee_id' or 'consignee' information must be provided."
            )
        
        # Validate that cities match the route
        self._validate_cities_match_route(data)
        
        # Check if shipment with this reference number already exists
        reference_number = data.get('reference_number')
        if reference_number:
            existing_shipment = repositories.shipment.get_latest_by_reference_number(reference_number)
            
            if existing_shipment:
                # Return the existing shipment data instead of creating new one
                data['existing_shipment'] = existing_shipment
                data['action'] = 'existing_shipment_found'
        
        return data
    
    def validate_shipment_type_id(self, value):
        """Validate that shipment type exists."""
        try:
            ShipmentType.objects.get(id=value)
        except ShipmentType.DoesNotExist:
            raise serializers.ValidationError("Shipment type with this ID does not exist.")
        return value 
    
    def validate_shipper_id(self, value):
        """Validate that shipper exists if provided."""
        if value is not None:
            try:
                Shipper.objects.get(id=value)
            except Shipper.DoesNotExist:
                raise serializers.ValidationError("Shipper with this ID does not exist.")
        return value
    
    def validate_consignee_id(self, value):
        """Validate that consignee exists if provided."""
        if value is not None:
            try:
                Consignee.objects.get(id=value)
            except Consignee.DoesNotExist:
                raise serializers.ValidationError("Consignee with this ID does not exist.")
        return value
    
    def _validate_cities_match_route(self, data):
        """Validate that a route exists from shipper's city to consignee's city."""
        
        # Get shipper city
        shipper_city = None
        if data.get('shipper_id'):
            try:
                shipper = Shipper.objects.get(id=data['shipper_id'])
                shipper_city = shipper.city
            except Shipper.DoesNotExist:
                raise serializers.ValidationError("Shipper with this ID does not exist.")
        elif data.get('shipper'):
            shipper_city = data['shipper'].get('city')
        
        # Get consignee city
        consignee_city = None
        if data.get('consignee_id'):
            try:
                consignee = Consignee.objects.get(id=data['consignee_id'])
                consignee_city = consignee.city
            except Consignee.DoesNotExist:
                raise serializers.ValidationError("Consignee with this ID does not exist.")
        elif data.get('consignee'):
            consignee_city = data['consignee'].get('city')
        
        # Validate that a route exists from shipper city to consignee city
        if shipper_city and consignee_city:
            route_exists = Route.objects.filter(
                origin__iexact=shipper_city,
                destination__iexact=consignee_city
            ).exists()
            
            if not route_exists:
                raise serializers.ValidationError(
                    f"No route found from '{shipper_city}' to '{consignee_city}'. "
                    f"Please check available routes or contact support."
                )
