from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Shipment, ShipmentLabel, Shipper, Consignee
from core.models import Courier, ShipmentType, Route


class ShipmentLabelViewTest(APITestCase):
    """Test cases for shipment label endpoint."""
    
    def setUp(self):
        """Set up test data."""
        # Create test courier
        self.courier = Courier.objects.create(
            name='DHL',
            is_active=True
        )
        
        # Create test shipment type
        self.shipment_type = ShipmentType.objects.create(
            name='Standard'
        )
        
        # Create test route
        self.route = Route.objects.create(
            origin='Berlin',
            destination='Munich'
        )
        
        # Create test shipper
        self.shipper = Shipper.objects.create(
            name='Test Shipper',
            address='Test Address',
            postal_code='12345',
            city='Berlin',
            country='Germany',
            phone='+49123456789',
            email='shipper@test.com'
        )
        
        # Create test consignee
        self.consignee = Consignee.objects.create(
            name='Test Consignee',
            address='Test Address',
            postal_code='54321',
            city='Munich',
            country='Germany',
            phone='+49987654321',
            email='consignee@test.com'
        )
        
        # Create test shipment
        self.shipment = Shipment.objects.create(
            courier=self.courier,
            shipment_type=self.shipment_type,
            courier_external_id='0034043333301020017016930',
            reference_number='TEST123',
            shipper=self.shipper,
            route=self.route,
            consignee=self.consignee,
            height=10,
            width=20,
            length=30,
            dimension_unit='cm',
            weight=1.5,
            weight_unit='kg'
        )
    
    def test_get_shipment_label_not_found(self):
        """Test getting label for non-existent shipment."""
        url = reverse('get_shipment_label', kwargs={'reference_number': 'NONEXISTENT'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error_code'], 'SHIPMENT_NOT_FOUND')
    
    def test_get_shipment_label_existing_label(self):
        """Test getting existing active label."""
        # Create existing label
        label = ShipmentLabel.objects.create(
            shipment=self.shipment,
            reference_number='TEST123',
            url='https://example.com/label.pdf',
            format='PDF',
            is_active=True
        )
        
        url = reverse('get_shipment_label', kwargs={'reference_number': 'TEST123'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['reference_number'], 'TEST123')
        self.assertEqual(response.data['data']['url'], 'https://example.com/label.pdf')
        self.assertEqual(response.data['data']['format'], 'PDF')
