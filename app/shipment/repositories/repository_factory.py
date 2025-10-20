"""Repository factory for easy access to all repositories."""

from .shipment_repository import ShipmentRepository
from .shipment_request_repository import ShipmentRequestRepository
from .shipment_label_repository import ShipmentLabelRepository
from .shipper_consignee_repository import ShipperRepository, ConsigneeRepository
from core.repositories.courier_repository import (
    CourierRepository,
    CourierConfigRepository,
    CourierShipmentTypeRepository,
    CourierRouteRepository,
    ShipmentTypeRepository,
    RouteRepository
)


class RepositoryFactory:
    """Factory class to provide access to all repositories."""
    
    def __init__(self):
        # Initialize all repositories
        self._shipment_repository = None
        self._shipment_request_repository = None
        self._shipment_label_repository = None
        self._shipper_repository = None
        self._consignee_repository = None
        self._courier_repository = None
        self._courier_config_repository = None
        self._courier_shipment_type_repository = None
        self._courier_route_repository = None
        self._shipment_type_repository = None
        self._route_repository = None
    
    @property
    def shipment(self) -> ShipmentRepository:
        """Get shipment repository."""
        if self._shipment_repository is None:
            self._shipment_repository = ShipmentRepository()
        return self._shipment_repository
    
    @property
    def shipment_request(self) -> ShipmentRequestRepository:
        """Get shipment request repository."""
        if self._shipment_request_repository is None:
            self._shipment_request_repository = ShipmentRequestRepository()
        return self._shipment_request_repository
    
    @property
    def shipment_label(self) -> ShipmentLabelRepository:
        """Get shipment label repository."""
        if self._shipment_label_repository is None:
            self._shipment_label_repository = ShipmentLabelRepository()
        return self._shipment_label_repository
    
    @property
    def shipper(self) -> ShipperRepository:
        """Get shipper repository."""
        if self._shipper_repository is None:
            self._shipper_repository = ShipperRepository()
        return self._shipper_repository
    
    @property
    def consignee(self) -> ConsigneeRepository:
        """Get consignee repository."""
        if self._consignee_repository is None:
            self._consignee_repository = ConsigneeRepository()
        return self._consignee_repository
    
    @property
    def courier(self) -> CourierRepository:
        """Get courier repository."""
        if self._courier_repository is None:
            self._courier_repository = CourierRepository()
        return self._courier_repository
    
    @property
    def courier_config(self) -> CourierConfigRepository:
        """Get courier config repository."""
        if self._courier_config_repository is None:
            self._courier_config_repository = CourierConfigRepository()
        return self._courier_config_repository
    
    @property
    def courier_shipment_type(self) -> CourierShipmentTypeRepository:
        """Get courier shipment type repository."""
        if self._courier_shipment_type_repository is None:
            self._courier_shipment_type_repository = CourierShipmentTypeRepository()
        return self._courier_shipment_type_repository
    
    @property
    def courier_route(self) -> CourierRouteRepository:
        """Get courier route repository."""
        if self._courier_route_repository is None:
            self._courier_route_repository = CourierRouteRepository()
        return self._courier_route_repository
    
    @property
    def shipment_type(self) -> ShipmentTypeRepository:
        """Get shipment type repository."""
        if self._shipment_type_repository is None:
            self._shipment_type_repository = ShipmentTypeRepository()
        return self._shipment_type_repository
    
    @property
    def route(self) -> RouteRepository:
        """Get route repository."""
        if self._route_repository is None:
            self._route_repository = RouteRepository()
        return self._route_repository


# Global repository factory instance
repositories = RepositoryFactory()
