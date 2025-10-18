from django.db import models


class Shipper(models.Model):
    """Model representing a shipper (sender) of shipments."""
    
    name = models.CharField(max_length=255, help_text="Name of the shipper")
    address = models.TextField(help_text="Address of the shipper")
    city = models.CharField(max_length=100, help_text="City of the shipper")
    country = models.CharField(max_length=100, help_text="Country of the shipper")
    phone = models.CharField(max_length=20, help_text="Phone number of the shipper")
    email = models.EmailField(help_text="Email address of the shipper")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shippers'
        ordering = ['name']
        verbose_name = 'Shipper'
        verbose_name_plural = 'Shippers'
    
    def __str__(self):
        return self.name


class Consignee(models.Model):
    """Model representing a consignee (receiver) of shipments."""
    
    name = models.CharField(max_length=255, help_text="Name of the consignee")
    address = models.TextField(help_text="Address of the consignee")
    city = models.CharField(max_length=100, help_text="City of the consignee")
    country = models.CharField(max_length=100, help_text="Country of the consignee")
    phone = models.CharField(max_length=20, help_text="Phone number of the consignee")
    email = models.EmailField(help_text="Email address of the consignee")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consignees'
        ordering = ['name']
        verbose_name = 'Consignee'
        verbose_name_plural = 'Consignees'
    
    def __str__(self):
        return self.name


class ShipmentRequest(models.Model):
    """Model representing shipment requests with retry logic."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    request_body = models.JSONField(help_text="JSON data of the shipment request")
    reference_number = models.CharField(help_text="Reference number of the shipment request", max_length=255)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Current status of the shipment request"
    )
    retries = models.PositiveIntegerField(
        default=0, 
        help_text="Number of retry attempts made"
    )
    last_retried_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Timestamp of the last retry attempt"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shipment_requests'
        ordering = ['-created_at']
        verbose_name = 'Shipment Request'
        verbose_name_plural = 'Shipment Requests'
    
    def __str__(self):
        return f"ShipmentRequest {self.id} - {self.status}"