# API Documentation

## Base URL
```
http://localhost:8000/api/v1/
```

## Endpoints

### 1. Create Shipment Request
**POST** `/shipment-requests/`

Creates a new shipment request.

**Request Body:**
```json
{
  "shipment_type_id": 1,
  "reference_number": "SHIP_001",
  "shipper_id": 1,
  "consignee_id": 1,
  "weight": 1.5,
  "weight_unit": "kg",
  "dimensions": {
    "height": 10,
    "width": 6,
    "length": 4
  },
  "dimension_unit": "cm",
  "items": [
    {
      "name": "Sample Item",
      "quantity": 1
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Shipment request created successfully",
  "data": {
    "id": 1,
    "reference_number": "SHIP_001",
    "status": "pending",
    "created_at": "2025-10-20T20:30:00.000000Z",
    "shipper_id": 1,
    "consignee_id": 1
  }
}
```

### 2. Get Shipment Label
**GET** `/shipment-labels/{reference_number}/`

Retrieves the shipping label for a shipment.

**Parameters:**
- `reference_number` (string): The shipment reference number

**Response:**
```json
{
  "success": true,
  "message": "Label retrieved successfully",
  "data": {
    "label_url": "https://example.com/label.pdf",
    "reference_number": "SHIP_001"
  }
}
```

### 3. Track Shipment
**GET** `/shipments/{reference_number}/track/`

Retrieves tracking information for a shipment.

**Parameters:**
- `reference_number` (string): The shipment reference number

**Response:**
```json
{
  "success": true,
  "tracking_number": "1234567890",
  "service": "DHL",
  "current_status": "in_transit",
  "status_description": "Package is in transit",
  "current_location": {
    "address": "Sorting Facility",
    "city": "Berlin",
    "country": "Germany",
    "postal_code": "10115"
  },
  "events": [
    {
      "timestamp": "2025-10-20T10:00:00Z",
      "status": "picked_up",
      "description": "Package picked up from sender",
      "location": {
        "address": "123 Main St",
        "city": "Bonn",
        "country": "Germany",
        "postal_code": "53111"
      }
    }
  ],
  "origin": {
    "address": "123 Main St",
    "city": "Bonn",
    "country": "Germany",
    "postal_code": "53111"
  },
  "destination": {
    "address": "456 Oak Ave",
    "city": "Berlin",
    "country": "Germany",
    "postal_code": "10115"
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error message",
  "error_code": "ERROR_CODE"
}
```

## Versioning

- **Current Version**: v1
- **Base URL**: `/api/v1/`
- **Future Versions**: v2, v3, etc. will be added as needed

## Migration from Unversioned API

Old endpoints (without versioning) are no longer available:
- ❌ `/api/shipment-requests/` → ✅ `/api/v1/shipment-requests/`
- ❌ `/api/shipment-labels/{ref}/` → ✅ `/api/v1/shipment-labels/{ref}/`
- ❌ `/api/shipments/{ref}/track/` → ✅ `/api/v1/shipments/{ref}/track/`
