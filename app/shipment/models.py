from django.db import models


class Shipment(models.Model):
    courier = models.ForeignKey(
        'core.Courier',
        on_delete=models.CASCADE
    )
    shipment_type = models.ForeignKey(
        'core.ShipmentType',
        on_delete=models.CASCADE
    )
    courier_external_id = models.CharField(
        max_length=255,
        unique=True
    )
    reference_number = models.CharField(
        max_length=255,
        unique=True
    )
    shipper = models.ForeignKey(
        'Shipper',
        on_delete=models.CASCADE
    )
    route = models.ForeignKey(
        'core.Route',
        on_delete=models.CASCADE
    )
    consignee = models.ForeignKey(
        'Consignee',
        on_delete=models.CASCADE
    )
    height = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    length = models.PositiveIntegerField()
    dimension_unit = models.CharField(
        max_length=10
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    weight_unit = models.CharField(
        max_length=10
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
    name = models.CharField(max_length=255)
    address = models.TextField()
    postal_code = models.CharField(max_length=25)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
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
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=25)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
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
    
    request_body = models.JSONField()
    reference_number = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    failed_reason = models.TextField(blank=True, null=True)
    retries = models.PositiveIntegerField(
        default=0
    )
    last_retried_at = models.DateTimeField(
        null=True, 
        blank=True
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
        on_delete=models.CASCADE
    )
    reference_number = models.CharField(
        max_length=255
    )
    url = models.URLField(
        max_length=500
    )
    format = models.CharField(
        max_length=50
    )
    is_active = models.BooleanField(
        default=True
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
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=100
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True
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