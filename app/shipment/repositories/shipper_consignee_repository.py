from typing import List, Optional
from ..models import Shipper, Consignee
from .base_repository import DjangoRepository


class ShipperRepository(DjangoRepository):
    """Repository for Shipper model operations."""
    
    def __init__(self):
        super().__init__(Shipper)
    
    def get_by_email(self, email: str) -> Optional[Shipper]:
        """Get shipper by email address."""
        return self.first(email=email)
    
    def get_by_city(self, city: str) -> List[Shipper]:
        """Get shippers by city."""
        return self.filter(city__iexact=city)
    
    def get_by_country(self, country: str) -> List[Shipper]:
        """Get shippers by country."""
        return self.filter(country__iexact=country)
    
    def get_or_create_by_email(self, email: str, defaults: dict = None) -> tuple[Shipper, bool]:
        """Get or create shipper by email."""
        if defaults is None:
            defaults = {}
        return self.get_or_create(email=email, defaults=defaults)
    
    def search_by_name(self, name: str) -> List[Shipper]:
        """Search shippers by name (case-insensitive)."""
        return self.filter(name__icontains=name)
    
    def get_active_shippers(self) -> List[Shipper]:
        """Get active shippers (if is_active field exists)."""
        if hasattr(self.model, 'is_active'):
            return self.filter(is_active=True)
        return self.get_all()


class ConsigneeRepository(DjangoRepository):
    """Repository for Consignee model operations."""
    
    def __init__(self):
        super().__init__(Consignee)
    
    def get_by_email(self, email: str) -> Optional[Consignee]:
        """Get consignee by email address."""
        return self.first(email=email)
    
    def get_by_city(self, city: str) -> List[Consignee]:
        """Get consignees by city."""
        return self.filter(city__iexact=city)
    
    def get_by_country(self, country: str) -> List[Consignee]:
        """Get consignees by country."""
        return self.filter(country__iexact=country)
    
    def get_or_create_by_email(self, email: str, defaults: dict = None) -> tuple[Consignee, bool]:
        """Get or create consignee by email."""
        if defaults is None:
            defaults = {}
        return self.get_or_create(email=email, defaults=defaults)
    
    def search_by_name(self, name: str) -> List[Consignee]:
        """Search consignees by name (case-insensitive)."""
        return self.filter(name__icontains=name)
    
    def get_active_consignees(self) -> List[Consignee]:
        """Get active consignees (if is_active field exists)."""
        if hasattr(self.model, 'is_active'):
            return self.filter(is_active=True)
        return self.get_all()
    
    def get_consignees_by_city_pair(self, origin_city: str, destination_city: str) -> List[Consignee]:
        """Get consignees in destination city for a specific route."""
        return self.filter(city__iexact=destination_city)
