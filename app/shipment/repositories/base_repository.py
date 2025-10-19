from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from django.db import models


class BaseRepository(ABC):
    """Base repository interface defining common CRUD operations."""
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[models.Model]:
        """Get a single record by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[models.Model]:
        """Get all records."""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> models.Model:
        """Create a new record."""
        pass
    
    @abstractmethod
    def update(self, id: int, **kwargs) -> Optional[models.Model]:
        """Update a record by ID."""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        pass
    
    @abstractmethod
    def filter(self, **kwargs) -> List[models.Model]:
        """Filter records by given criteria."""
        pass
    
    @abstractmethod
    def get_or_create(self, defaults: Dict[str, Any] = None, **kwargs) -> tuple[models.Model, bool]:
        """Get or create a record."""
        pass


class DjangoRepository(BaseRepository):
    """Base Django repository implementation."""
    
    def __init__(self, model_class: models.Model):
        self.model = model_class
    
    def get_by_id(self, id: int) -> Optional[models.Model]:
        """Get a single record by ID."""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def get_all(self) -> List[models.Model]:
        """Get all records."""
        return list(self.model.objects.all())
    
    def create(self, **kwargs) -> models.Model:
        """Create a new record."""
        return self.model.objects.create(**kwargs)
    
    def update(self, id: int, **kwargs) -> Optional[models.Model]:
        """Update a record by ID."""
        try:
            obj = self.model.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
            return obj
        except self.model.DoesNotExist:
            return None
    
    def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        try:
            obj = self.model.objects.get(id=id)
            obj.delete()
            return True
        except self.model.DoesNotExist:
            return False
    
    def filter(self, **kwargs) -> List[models.Model]:
        """Filter records by given criteria."""
        return list(self.model.objects.filter(**kwargs))
    
    def get_or_create(self, defaults: Dict[str, Any] = None, **kwargs) -> tuple[models.Model, bool]:
        """Get or create a record."""
        if defaults is None:
            defaults = {}
        return self.model.objects.get_or_create(defaults=defaults, **kwargs)
    
    def exists(self, **kwargs) -> bool:
        """Check if a record exists with given criteria."""
        return self.model.objects.filter(**kwargs).exists()
    
    def count(self, **kwargs) -> int:
        """Count records matching given criteria."""
        return self.model.objects.filter(**kwargs).count()
    
    def first(self, **kwargs) -> Optional[models.Model]:
        """Get the first record matching given criteria."""
        try:
            return self.model.objects.filter(**kwargs).first()
        except self.model.DoesNotExist:
            return None
    
    def last(self, **kwargs) -> Optional[models.Model]:
        """Get the last record matching given criteria."""
        try:
            return self.model.objects.filter(**kwargs).last()
        except self.model.DoesNotExist:
            return None
