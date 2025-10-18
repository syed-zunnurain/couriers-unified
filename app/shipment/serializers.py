from rest_framework import serializers
from core.models import ShipmentType, Route
from .models import Shipper, Consignee, ShipmentRequest


class ShipperSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating shippers."""
    
    class Meta:
        model = Shipper
        fields = ['name', 'address', 'city', 'country', 'phone', 'email']


class ConsigneeSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating consignees."""
    
    class Meta:
        model = Consignee
        fields = ['name', 'address', 'city', 'country', 'phone', 'email']


class ShipmentRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating shipment requests."""
    
    # Required fields
    shipment_type_id = serializers.IntegerField()
    route_id = serializers.IntegerField()
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
    pickup_date = serializers.DateField()
    weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    dimensions = serializers.DictField(
        help_text="Dimensions in format: {length: 10, width: 5, height: 3}"
    )
    special_instructions = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Special instructions for the shipment"
    )
    
    def validate(self, data):
        """Validate that either shipper_id or shipper data is provided."""
        if not data.get('shipper_id') and not data.get('shipper'):
            raise serializers.ValidationError(
                "Either 'shipper_id' or 'shipper' information must be provided."
            )
        
        if not data.get('consignee_id') and not data.get('consignee'):
            raise serializers.ValidationError(
                "Either 'consignee_id' or 'consignee' information must be provided."
            )
        
        return data
    
    def validate_shipment_type_id(self, value):
        """Validate that shipment type exists."""
        try:
            ShipmentType.objects.get(id=value)
        except ShipmentType.DoesNotExist:
            raise serializers.ValidationError("Shipment type with this ID does not exist.")
        return value
    
    def validate_route_id(self, value):
        """Validate that route exists."""
        try:
            Route.objects.get(id=value)
        except Route.DoesNotExist:
            raise serializers.ValidationError("Route with this ID does not exist.")
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
