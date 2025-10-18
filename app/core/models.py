
from django.db import models


class Courier(models.Model):
    """Model representing a courier service provider."""
    
    name = models.CharField(max_length=255, unique=True, help_text="Name of the courier service")
    supports_cancellation = models.BooleanField(
        default=False, 
        help_text="Whether this courier supports order cancellation"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this courier is currently active"
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
    """Model representing different types of shipments."""
    
    name = models.CharField(max_length=100, unique=True, help_text="Name of the shipment type (e.g., normal, urgent)")
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
    """Model representing the many-to-many relationship between couriers and shipment types."""
    
    courier = models.ForeignKey(
        Courier, 
        on_delete=models.CASCADE,
        help_text="The courier service"
    )
    shipment_type = models.ForeignKey(
        ShipmentType, 
        on_delete=models.CASCADE,
        help_text="The shipment type supported by this courier"
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
    """Model representing shipping routes between origin and destination."""
    
    origin = models.CharField(max_length=255, help_text="Origin location of the route")
    destination = models.CharField(max_length=255, help_text="Destination location of the route")
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
    """Model representing the many-to-many relationship between couriers and routes."""
    
    courier = models.ForeignKey(
        Courier, 
        on_delete=models.CASCADE,
        help_text="The courier service"
    )
    route = models.ForeignKey(
        Route, 
        on_delete=models.CASCADE,
        help_text="The route supported by this courier"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this route is currently active for this courier"
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
    """Model representing courier configuration settings."""
    
    courier = models.ForeignKey(
        Courier, 
        on_delete=models.CASCADE,
        help_text="The courier this configuration belongs to"
    )
    base_url = models.URLField(
        help_text="Base URL for the courier's API"
    )
    api_key = models.CharField(
        max_length=500, 
        help_text="API key for authentication"
    )
    api_secret = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text="API secret for authentication (optional)"
    )
    username = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Username for authentication (optional)"
    )
    password = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Password for authentication (optional)"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this configuration is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courier_configs'
        ordering = ['courier__name']
        verbose_name = 'Courier Configuration'
        verbose_name_plural = 'Courier Configurations'
        unique_together = ['courier']  # One config per courier
    
    def __str__(self):
        return f"{self.courier.name} Configuration"
