from django.db import models


class Shipment(models.Model):
    courier = models.ForeignKey(
        'core.Courier',
        on_delete=models.CASCADE,
        help_text="The courier service handling this shipment"
    )
    shipment_type = models.ForeignKey(
        'core.ShipmentType',
        on_delete=models.CASCADE,
        help_text="The type of shipment"
    )
    courier_external_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="External ID provided by the courier service"
    )
    reference_number = models.CharField(
        max_length=255,
        unique=True,
        help_text="Reference number for this shipment"
    )
    shipper = models.ForeignKey(
        'Shipper',
        on_delete=models.CASCADE,
        help_text="The shipper (sender) of this shipment"
    )
    route = models.ForeignKey(
        'core.Route',
        on_delete=models.CASCADE,
        help_text="The route of this shipment"
    )
    consignee = models.ForeignKey(
        'Consignee',
        on_delete=models.CASCADE,
        help_text="The consignee (receiver) of this shipment"
    )
    height = models.PositiveIntegerField(
        help_text="Height of the shipment"
    )
    width = models.PositiveIntegerField(
        help_text="Width of the shipment"
    )
    length = models.PositiveIntegerField(
        help_text="Length of the shipment"
    )
    dimension_unit = models.CharField(
        max_length=10,
        help_text="Unit of measurement for dimensions (e.g., cm, in)"
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Weight of the shipment"
    )
    weight_unit = models.CharField(
        max_length=10,
        help_text="Unit of measurement for weight (e.g., kg, lb)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shipments'
        ordering = ['-created_at']
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
    
    def __str__(self):
        return f"Shipment {self.id} - {self.reference_number}"


class Shipper(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the shipper")
    address = models.TextField(help_text="Address of the shipper")
    postal_code = models.CharField(max_length=25, help_text="Postal code of the shipper")
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
    name = models.CharField(max_length=255, help_text="Name of the consignee")
    address = models.TextField(help_text="Address of the consignee")
    city = models.CharField(max_length=100, help_text="City of the consignee")
    postal_code = models.CharField(max_length=25, help_text="Postal code of the consignee")
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
    failed_reason = models.TextField(blank=True, help_text='Reason for failure', null=True)
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


class ShipmentLabel(models.Model):
    shipment = models.ForeignKey(
        'Shipment',
        on_delete=models.CASCADE,
        help_text="The shipment this label belongs to"
    )
    reference_number = models.CharField(
        max_length=255,
        help_text="Reference number for this label"
    )
    url = models.URLField(
        max_length=500,
        help_text="URL to download the label"
    )
    format = models.CharField(
        max_length=50,
        help_text="Format of the label (e.g., PDF, PNG, ZPL)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this label is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shipment_labels'
        ordering = ['-created_at']
        verbose_name = 'Shipment Label'
        verbose_name_plural = 'Shipment Labels'
        indexes = [
            models.Index(fields=['shipment_id']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"ShipmentLabel {self.id} - {self.reference_number}"


class ShipmentStatus(models.Model):
    shipment = models.ForeignKey(
        'Shipment',
        on_delete=models.CASCADE,
        help_text="The shipment this status update belongs to"
    )
    status = models.CharField(
        max_length=100,
        help_text="Current status of the shipment (e.g., in_transit, delivered, exception)"
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Address where the status update occurred"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Postal code of the location"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Country where the status update occurred"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shipment_statuses'
        ordering = ['-created_at']
        verbose_name = 'Shipment Status'
        verbose_name_plural = 'Shipment Statuses'
        indexes = [
            models.Index(fields=['shipment_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"ShipmentStatus {self.id} - {self.shipment.reference_number} - {self.status}"