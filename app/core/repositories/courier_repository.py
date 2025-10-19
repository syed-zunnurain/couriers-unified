from typing import List, Optional
from ..models import Courier, CourierConfig, CourierShipmentType, CourierRoute, ShipmentType, Route
from shipment.repositories.base_repository import DjangoRepository


class CourierRepository(DjangoRepository):
    """Repository for Courier model operations."""
    
    def __init__(self):
        super().__init__(Courier)
    
    def get_active_couriers(self) -> List[Courier]:
        """Get all active couriers."""
        return self.filter(is_active=True)
    
    def get_by_name(self, name: str) -> Optional[Courier]:
        """Get courier by name (case-insensitive)."""
        return self.first(name__iexact=name)
    
    def get_courier_with_config(self, courier_name: str) -> Optional[Courier]:
        """Get courier with its configuration."""
        try:
            return self.model.objects.select_related().get(
                name__iexact=courier_name,
                is_active=True
            )
        except self.model.DoesNotExist:
            return None


class CourierConfigRepository(DjangoRepository):
    """Repository for CourierConfig model operations."""
    
    def __init__(self):
        super().__init__(CourierConfig)
    
    def get_active_configs(self) -> List[CourierConfig]:
        """Get all active courier configurations."""
        return self.filter(is_active=True)
    
    def get_by_courier_name(self, courier_name: str) -> Optional[CourierConfig]:
        """Get courier configuration by courier name."""
        try:
            return self.model.objects.select_related('courier').get(
                courier__name__iexact=courier_name,
                is_active=True
            )
        except self.model.DoesNotExist:
            return None
    
    def get_by_courier_id(self, courier_id: int) -> Optional[CourierConfig]:
        """Get courier configuration by courier ID."""
        return self.first(courier_id=courier_id, is_active=True)


class CourierShipmentTypeRepository(DjangoRepository):
    """Repository for CourierShipmentType model operations."""
    
    def __init__(self):
        super().__init__(CourierShipmentType)
    
    def get_by_shipment_type(self, shipment_type_id: int) -> List[CourierShipmentType]:
        """Get courier shipment types by shipment type ID."""
        return self.filter(
            shipment_type_id=shipment_type_id,
            courier__is_active=True
        )
    
    def get_by_courier(self, courier_id: int) -> List[CourierShipmentType]:
        """Get courier shipment types by courier ID."""
        return self.filter(courier_id=courier_id)
    
    def get_available_couriers_for_shipment_type(self, shipment_type_id: int) -> List[int]:
        """Get courier IDs available for a specific shipment type."""
        return list(
            self.model.objects.filter(
                shipment_type_id=shipment_type_id,
                courier__is_active=True
            ).values_list('courier_id', flat=True)
        )


class CourierRouteRepository(DjangoRepository):
    """Repository for CourierRoute model operations."""
    
    def __init__(self):
        super().__init__(CourierRoute)
    
    def get_by_route(self, origin_city: str, destination_city: str) -> List[CourierRoute]:
        """Get courier routes by origin and destination cities."""
        return self.filter(
            route__origin__iexact=origin_city,
            route__destination__iexact=destination_city,
            is_active=True,
            courier__is_active=True
        )
    
    def get_by_courier(self, courier_id: int) -> List[CourierRoute]:
        """Get courier routes by courier ID."""
        return self.filter(courier_id=courier_id, is_active=True)
    
    def get_available_couriers_for_route(self, origin_city: str, destination_city: str) -> List[int]:
        """Get courier IDs available for a specific route."""
        return list(
            self.model.objects.filter(
                route__origin__iexact=origin_city,
                route__destination__iexact=destination_city,
                is_active=True,
                courier__is_active=True
            ).values_list('courier_id', flat=True)
        )


class ShipmentTypeRepository(DjangoRepository):
    """Repository for ShipmentType model operations."""
    
    def __init__(self):
        super().__init__(ShipmentType)
    
    def get_by_name(self, name: str) -> Optional[ShipmentType]:
        """Get shipment type by name."""
        return self.first(name__iexact=name)
    
    def get_active_types(self) -> List[ShipmentType]:
        """Get active shipment types."""
        if hasattr(self.model, 'is_active'):
            return self.filter(is_active=True)
        return self.get_all()


class RouteRepository(DjangoRepository):
    """Repository for Route model operations."""
    
    def __init__(self):
        super().__init__(Route)
    
    def get_by_cities(self, origin: str, destination: str) -> Optional[Route]:
        """Get route by origin and destination cities."""
        return self.first(
            origin__iexact=origin,
            destination__iexact=destination
        )
    
    def get_or_create_by_cities(self, origin: str, destination: str) -> tuple[Route, bool]:
        """Get or create route by origin and destination cities."""
        return self.get_or_create(
            origin=origin,
            destination=destination
        )
    
    def get_routes_by_origin(self, origin: str) -> List[Route]:
        """Get all routes from a specific origin city."""
        return self.filter(origin__iexact=origin)
    
    def get_routes_by_destination(self, destination: str) -> List[Route]:
        """Get all routes to a specific destination city."""
        return self.filter(destination__iexact=destination)
