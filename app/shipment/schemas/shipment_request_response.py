from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ShipmentRequestData:
    """Data structure for shipment request response."""
    id: int
    reference_number: str
    status: str
    created_at: datetime
    shipper_id: int
    consignee_id: int


@dataclass
class ExistingShipmentData:
    """Data structure for existing shipment response."""
    id: int
    reference_number: str
    courier: str
    status: str
    created_at: datetime


@dataclass
class ShipmentRequestResponse:
    """Response schema for create shipment request endpoint."""
    success: bool
    message: str
    data: ShipmentRequestData | ExistingShipmentData
    status_code: int = 200

    # Response configuration
    RESPONSE_CONFIG = {
        'new': {
            'message': "Shipment request created successfully",
            'status_code': 201,
            'data_type': 'ShipmentRequestData'
        },
        'existing_shipment': {
            'message': "Shipment with this reference number already exists",
            'status_code': 200,
            'data_type': 'ExistingShipmentData'
        },
        'already_processing': {
            'message': "Shipment request with this reference number is already under process",
            'status_code': 200,
            'data_type': 'ShipmentRequestData'
        }
    }

    @classmethod
    def create_response(cls, 
                       response_type: str,
                       shipment_request=None,
                       existing_shipment=None,
                       shipper_id: int = None,
                       consignee_id: int = None) -> 'ShipmentRequestResponse':
        """
        Create response for shipment request endpoint.
        
        Args:
            response_type: Type of response ('new', 'existing_shipment', 'already_processing')
            shipment_request: ShipmentRequest object (for 'new' and 'already_processing')
            existing_shipment: Shipment object (for 'existing_shipment')
            shipper_id: Shipper ID (for 'new' and 'already_processing')
            consignee_id: Consignee ID (for 'new' and 'already_processing')
        """
        config = cls.RESPONSE_CONFIG.get(response_type)
        if not config:
            raise ValueError(f"Invalid response_type: {response_type}")

        # Create data based on response type
        if response_type == 'existing_shipment':
            data = ExistingShipmentData(
                id=existing_shipment.id,
                reference_number=existing_shipment.reference_number,
                courier=existing_shipment.courier.name,
                status="completed",
                created_at=existing_shipment.created_at
            )
        else:  # 'new' or 'already_processing'
            # Get shipper/consignee IDs - use provided values or extract from request_body
            final_shipper_id = shipper_id or shipment_request.request_body.get('shipper_id')
            final_consignee_id = consignee_id or shipment_request.request_body.get('consignee_id')
            
            data = ShipmentRequestData(
                id=shipment_request.id,
                reference_number=shipment_request.reference_number,
                status=shipment_request.status,
                created_at=shipment_request.created_at,
                shipper_id=final_shipper_id,
                consignee_id=final_consignee_id
            )

        return cls(
            success=True,
            message=config['message'],
            data=data,
            status_code=config['status_code']
        )

    def to_dict(self) -> dict:
        """Convert response to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'message': self.message,
            'data': {
                'id': self.data.id,
                'reference_number': self.data.reference_number,
                'status': self.data.status,
                'created_at': self.data.created_at.isoformat() if isinstance(self.data.created_at, datetime) else self.data.created_at,
                **self._get_additional_data()
            }
        }

    def _get_additional_data(self) -> dict:
        """Get additional data based on response type."""
        if isinstance(self.data, ExistingShipmentData):
            return {
                'courier': self.data.courier
            }
        elif isinstance(self.data, ShipmentRequestData):
            return {
                'shipper_id': self.data.shipper_id,
                'consignee_id': self.data.consignee_id
            }
        return {}
