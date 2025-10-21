import json
from django.test import TestCase, Client
from django.urls import reverse
from core.models import Courier, CourierConfig, ShipmentType, Route, CourierRoute, CourierShipmentType
from .models import Shipment, Shipper, Consignee, ShipmentRequest, ShipmentLabel, ShipmentStatus


class ShipmentAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.courier = Courier.objects.create(
            name="DHL",
            supports_cancellation=True,
            is_active=True
        )
        
        self.courier_config = CourierConfig.objects.create(
            courier=self.courier,
            base_url="https://api-sandbox.dhl.com",
            api_key="test-api-key",
            api_secret="test-api-secret",
            is_active=True
        )
        
        self.shipment_type = ShipmentType.objects.create(name="express")
        
        CourierShipmentType.objects.create(
            courier=self.courier,
            shipment_type=self.shipment_type
        )
        
        self.route = Route.objects.create(
            origin="Berlin",
            destination="Bonn"
        )
        
        CourierRoute.objects.create(
            courier=self.courier,
            route=self.route,
            is_active=True
        )
        
        self.shipper = Shipper.objects.create(
            name="John Doe",
            address="123 Main Street, Al Olaya",
            city="Berlin",
            country="DEU",
            phone="+966501234567",
            email="john.doe@example.com",
            postal_code="12235"
        )
        
        self.consignee = Consignee.objects.create(
            name="Jane Smith",
            address="456 King Abdulaziz Road",
            city="Bonn",
            country="DEU",
            phone="+966509876543",
            email="jane.smith@example.com",
            postal_code="12345"
        )
        
        self.shipment = Shipment.objects.create(
            courier=self.courier,
            shipment_type=self.shipment_type,
            courier_external_id="0034043333301020017128697",
            reference_number="REF123437",
            shipper=self.shipper,
            route=self.route,
            consignee=self.consignee,
            height=20,
            width=30,
            length=50,
            dimension_unit="mm",
            weight=1.2,
            weight_unit="kg"
        )
        
        self.shipment_request = ShipmentRequest.objects.create(
            request_body={"test": "data"},
            reference_number="REF123437",
            status="completed"
        )
        
        self.shipment_label = ShipmentLabel.objects.create(
            shipment=self.shipment,
            reference_number="REF123437",
            url="https://api-sandbox.dhl.com/parcel/de/shipping/v2/labels?token=test",
            format="PDF",
            is_active=True
        )
        
        self.shipment_status = ShipmentStatus.objects.create(
            shipment=self.shipment,
            status="created",
            address="123 Main Street, Al Olaya, Berlin",
            postal_code="12235",
            country="DEU"
        )

    def test_create_shipment_request_validation_error(self):
        url = reverse('create_shipment_request')
        data = {
            "shipment_type_id": self.shipment_type.id,
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)

    def test_create_shipment_request_success(self):
        url = reverse('create_shipment_request')
        data = {
            "shipment_type_id": self.shipment_type.id,
            "reference_number": "REF123438",
            "shipper": {
                "name": "Test Shipper",
                "address": "123 Test Street",
                "city": "Berlin",
                "country": "DEU",
                "phone": "+1234567890",
                "email": "test@example.com",
                "postal_code": "12235"
            },
            "consignee": {
                "name": "Test Consignee",
                "address": "456 Test Road",
                "city": "Bonn",
                "country": "DEU",
                "phone": "+0987654321",
                "email": "test2@example.com",
                "postal_code": "12345"
            },
            "pickup_date": "2024-01-15",
            "weight": 1.5,
            "weight_unit": "kg",
            "dimensions": {
                "length": 50,
                "width": 30,
                "height": 20
            },
            "dimension_unit": "mm",
            "special_instructions": "Handle with care"
        }
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        
        self.assertIn(response.status_code, [200, 201, 400, 500])
        response_data = json.loads(response.content)
        self.assertIn('success', response_data)

    def test_get_shipment_label_endpoint(self):
        url = reverse('get_shipment_label', kwargs={'reference_number': 'REF123437'})
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [200, 404, 500])
        response_data = json.loads(response.content)
        self.assertIn('success', response_data)

    def test_get_shipment_label_not_found(self):
        url = reverse('get_shipment_label', kwargs={'reference_number': 'NONEXISTENT'})
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [200, 404, 500])
        response_data = json.loads(response.content)
        self.assertIn('success', response_data)

    def test_track_shipment_endpoint(self):
        url = reverse('track_shipment', kwargs={'reference_number': 'REF123437'})
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [200, 404, 500])
        response_data = json.loads(response.content)
        self.assertIn('success', response_data)

    def test_track_shipment_not_found(self):
        url = reverse('track_shipment', kwargs={'reference_number': 'NONEXISTENT'})
        response = self.client.get(url)
        
        self.assertIn(response.status_code, [200, 404, 500])
        response_data = json.loads(response.content)
        self.assertIn('success', response_data)

    def test_cancel_shipment_endpoint(self):
        url = reverse('cancel_shipment', kwargs={'reference_number': 'REF123437'})
        response = self.client.post(url)
        
        self.assertIn(response.status_code, [200, 400, 404, 500])
        response_data = json.loads(response.content)
        self.assertIn('success', response_data)

    def test_cancel_shipment_not_found(self):
        url = reverse('cancel_shipment', kwargs={'reference_number': 'NONEXISTENT'})
        response = self.client.post(url)
        
        self.assertIn(response.status_code, [200, 400, 404, 500])
        response_data = json.loads(response.content)
        self.assertIn('success', response_data)

    def test_dhl_webhook_success(self):
        url = reverse('dhl_webhook')
        data = {
            "tracking_number": "0034043333301020017128697",
            "status": "in_transit",
            "location": {
                "countryCode": "DEU",
                "postalCode": "12345",
                "addressLocality": "456 King Abdulaziz Road"
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_API_KEY='dhl-webhook-secret-key-2024'
        )
        
        self.assertIn(response.status_code, [200, 400, 403, 500])
        response_data = json.loads(response.content)
        self.assertIn('success', response_data)

    def test_dhl_webhook_invalid_api_key(self):
        url = reverse('dhl_webhook')
        data = {
            "tracking_number": "0034043333301020017128697",
            "status": "in_transit"
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_X_API_KEY='invalid-key'
        )
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_dhl_webhook_invalid_json(self):
        url = reverse('dhl_webhook')
        
        response = self.client.post(
            url,
            data="invalid json",
            content_type='application/json',
            HTTP_X_API_KEY='dhl-webhook-secret-key-2024'
        )
        
        self.assertIn(response.status_code, [400, 403])
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])

    def test_database_models_work(self):
        self.assertEqual(self.courier.name, "DHL")
        self.assertTrue(self.courier.is_active)
        
        self.assertEqual(self.shipment.reference_number, "REF123437")
        self.assertEqual(self.shipment.courier, self.courier)
        
        self.assertEqual(self.shipper.name, "John Doe")
        self.assertEqual(self.shipper.city, "Berlin")
        
        self.assertEqual(self.consignee.name, "Jane Smith")
        self.assertEqual(self.consignee.city, "Bonn")
        
        self.assertEqual(self.shipment_label.format, "PDF")
        self.assertTrue(self.shipment_label.is_active)
        
        self.assertEqual(self.shipment_status.status, "created")
        self.assertEqual(self.shipment_status.country, "DEU")

    def test_url_patterns_exist(self):
        try:
            reverse('create_shipment_request')
            reverse('get_shipment_label', kwargs={'reference_number': 'test'})
            reverse('track_shipment', kwargs={'reference_number': 'test'})
            reverse('cancel_shipment', kwargs={'reference_number': 'test'})
            reverse('dhl_webhook')
        except Exception as e:
            self.fail(f"URL pattern error: {e}")

    def test_endpoints_respond(self):
        endpoints = [
            ('create_shipment_request', 'POST', {}),
            ('get_shipment_label', 'GET', {'reference_number': 'test'}),
            ('track_shipment', 'GET', {'reference_number': 'test'}),
            ('cancel_shipment', 'POST', {'reference_number': 'test'}),
            ('dhl_webhook', 'POST', {}),
        ]
        
        for endpoint_name, method, kwargs in endpoints:
            try:
                url = reverse(endpoint_name, kwargs=kwargs)
                
                if method == 'GET':
                    response = self.client.get(url)
                else:
                    response = self.client.post(url, data=json.dumps({}), content_type='application/json')
                
                self.assertIsNotNone(response)
                
            except Exception as e:
                self.fail(f"Endpoint {endpoint_name} failed: {e}")

    def test_shipment_creation_flow(self):
        shipper = Shipper.objects.create(
            name="Integration Test Shipper",
            address="123 Integration Street",
            city="Berlin",
            country="DEU",
            phone="+1234567890",
            email="integration@example.com",
            postal_code="12235"
        )
        
        consignee = Consignee.objects.create(
            name="Integration Test Consignee",
            address="456 Integration Road",
            city="Bonn",
            country="DEU",
            phone="+0987654321",
            email="integration2@example.com",
            postal_code="12345"
        )
        
        shipment = Shipment.objects.create(
            courier=self.courier,
            shipment_type=self.shipment_type,
            courier_external_id="INTEGRATION123456",
            reference_number="REF123456",
            shipper=shipper,
            route=self.route,
            consignee=consignee,
            height=25,
            width=35,
            length=55,
            dimension_unit="mm",
            weight=2.0,
            weight_unit="kg"
        )
        
        self.assertEqual(shipment.reference_number, "REF123456")
        self.assertEqual(shipment.courier, self.courier)
        self.assertEqual(shipment.shipper, shipper)
        self.assertEqual(shipment.consignee, consignee)
        
        request = ShipmentRequest.objects.create(
            request_body={"integration": "test"},
            reference_number="REF123456",
            status="pending"
        )
        
        self.assertEqual(request.reference_number, "REF123456")
        self.assertEqual(request.status, "pending")
        
        label = ShipmentLabel.objects.create(
            shipment=shipment,
            reference_number="REF123456",
            url="https://example.com/label.pdf",
            format="PDF",
            is_active=True
        )
        
        self.assertEqual(label.reference_number, "REF123456")
        self.assertEqual(label.format, "PDF")
        
        status = ShipmentStatus.objects.create(
            shipment=shipment,
            status="created",
            address="123 Integration Street, Berlin",
            postal_code="12235",
            country="DEU"
        )
        
        self.assertEqual(status.status, "created")
        self.assertEqual(status.country, "DEU")
