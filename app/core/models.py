
from django.db import models
from .utils.encryption import encryption_manager


class Courier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    supports_cancellation = models.BooleanField(
        default=False
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'couriers'
        ordering = ['name']
        verbose_name = 'Courier'
        verbose_name_plural = 'Couriers'
    
    def __str__(self):
        return self.name


class ShipmentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shipment_types'
        ordering = ['name']
        verbose_name = 'Shipment Type'
        verbose_name_plural = 'Shipment Types'
    
    def __str__(self):
        return self.name


class CourierShipmentType(models.Model):
    courier = models.ForeignKey(
        Courier, 
        on_delete=models.CASCADE
    )
    shipment_type = models.ForeignKey(
        ShipmentType, 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courier_shipment_types'
        unique_together = ['courier', 'shipment_type']
        ordering = ['courier__name', 'shipment_type__name']
        verbose_name = 'Courier Shipment Type'
        verbose_name_plural = 'Courier Shipment Types'
    
    def __str__(self):
        return f"{self.courier.name} - {self.shipment_type.name}"


class Route(models.Model):
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'routes'
        ordering = ['origin', 'destination']
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'
    
    def __str__(self):
        return f"{self.origin} → {self.destination}"


class CourierRoute(models.Model):
    courier = models.ForeignKey(
        Courier, 
        on_delete=models.CASCADE
    )
    route = models.ForeignKey(
        Route, 
        on_delete=models.CASCADE
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courier_routes'
        unique_together = ['courier', 'route']
        ordering = ['courier__name', 'route__origin', 'route__destination']
        verbose_name = 'Courier Route'
        verbose_name_plural = 'Courier Routes'
    
    def __str__(self):
        return f"{self.courier.name} - {self.route.origin} → {self.route.destination}"


class CourierConfig(models.Model):
    courier = models.ForeignKey(
        Courier, 
        on_delete=models.CASCADE
    )
    base_url = models.URLField()
    _api_key = models.TextField()
    _api_secret = models.TextField(
        blank=True, 
        null=True
    )
    _username = models.TextField(
        blank=True, 
        null=True
    )
    _password = models.TextField(
        blank=True, 
        null=True
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courier_configs'
        ordering = ['courier__name']
        verbose_name = 'Courier Configuration'
        verbose_name_plural = 'Courier Configurations'
        unique_together = ['courier']
    
    def __str__(self):
        return f"{self.courier.name} Configuration"
    
    @property
    def api_key(self):
        return encryption_manager.decrypt(self._api_key) if self._api_key else ""
    
    @api_key.setter
    def api_key(self, value):
        self._api_key = encryption_manager.encrypt(value) if value else ""
    
    @property
    def api_secret(self):
        return encryption_manager.decrypt(self._api_secret) if self._api_secret else ""
    
    @api_secret.setter
    def api_secret(self, value):
        self._api_secret = encryption_manager.encrypt(value) if value else ""
    
    @property
    def username(self):
        return encryption_manager.decrypt(self._username) if self._username else ""
    
    @username.setter
    def username(self, value):
        self._username = encryption_manager.encrypt(value) if value else ""
    
    @property
    def password(self):
        return encryption_manager.decrypt(self._password) if self._password else ""
    
    @password.setter
    def password(self, value):
        self._password = encryption_manager.encrypt(value) if value else ""
