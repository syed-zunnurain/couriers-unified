# Couriers Unified - Multi-Courier Integration Framework

A unified framework for integrating multiple courier services (35+ couriers) with a standardized interface, built with Django and Python following SOLID principles.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Key Features](#key-features)
- [Design Decisions](#design-decisions)
- [Installation & Setup](#installation--setup)
- [Usage Examples](#usage-examples)
- [Sequence Diagrams](#sequence-diagrams)
- [Contributing](#contributing)

## Overview

This framework provides a unified interface for integrating with multiple courier services, eliminating the need to custom implement each courier integration independently. The system supports core courier operations including shipment creation, label printing, tracking, and optional cancellation functionality.

### Core Features

- **Unified Interface**: Single API for all courier operations
- **Modular Design**: Easy to add new couriers without changing existing code
- **Retry Logic**: Built-in HTTP retry mechanisms for reliability
- **Status Mapping**: Automatic mapping of courier-specific statuses to system statuses
- **Webhook Support**: Real-time status updates from couriers
- **Encryption**: Secure storage of courier credentials
- **Async Processing**: Background workers for handling shipment requests

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        API[REST API]
        WEBHOOK[Webhook Endpoints]
    end
    
    subgraph "Application Layer"
        VIEWS[Django Views]
        SERIALIZERS[Serializers]
        SERVICES[Service Layer]
    end
    
    subgraph "Business Logic Layer"
        COURIER_FACTORY[Courier Factory]
        REQUEST_SERVICE[Request Service]
        LABEL_SERVICE[Label Service]
        TRACKING_SERVICE[Tracking Service]
        CANCELLATION_SERVICE[Cancellation Service]
    end
    
    subgraph "Courier Integration Layer"
        BASE_COURIER[Base Courier]
        DHL_COURIER[DHL Courier]
        FUTURE_COURIER[Future Couriers...]
        HTTP_CLIENTS[HTTP Clients]
    end
    
    subgraph "Data Layer"
        REPOSITORIES[Repository Pattern]
        MODELS[Django Models]
        DATABASE[(PostgreSQL)]
    end
    
    subgraph "External Services"
        DHL_API[DHL API]
        OTHER_APIS[Other Courier APIs]
    end
    
    subgraph "Background Processing"
        WORKER[Background Worker]
        QUEUE[Message Queue]
    end
    
    API --> VIEWS
    WEBHOOK --> VIEWS
    VIEWS --> SERIALIZERS
    SERIALIZERS --> SERVICES
    SERVICES --> COURIER_FACTORY
    COURIER_FACTORY --> BASE_COURIER
    BASE_COURIER --> DHL_COURIER
    BASE_COURIER --> FUTURE_COURIER
    DHL_COURIER --> HTTP_CLIENTS
    HTTP_CLIENTS --> DHL_API
    HTTP_CLIENTS --> OTHER_APIS
    SERVICES --> REPOSITORIES
    REPOSITORIES --> MODELS
    MODELS --> DATABASE
    WORKER --> QUEUE
    QUEUE --> SERVICES
```

### Component Overview

1. **API Layer**: RESTful endpoints for shipment operations
2. **Service Layer**: Business logic and orchestration
3. **Courier Integration Layer**: Abstracted courier implementations
4. **Data Layer**: Repository pattern with Django ORM
5. **Background Processing**: Async workers for heavy operations

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    Courier {
        int id PK
        string name UK
        boolean supports_cancellation
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    ShipmentType {
        int id PK
        string name UK
        datetime created_at
        datetime updated_at
    }
    
    CourierShipmentType {
        int id PK
        int courier_id FK
        int shipment_type_id FK
        datetime created_at
        datetime updated_at
    }
    
    Route {
        int id PK
        string origin
        string destination
        datetime created_at
        datetime updated_at
    }
    
    CourierRoute {
        int id PK
        int courier_id FK
        int route_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    CourierConfig {
        int id PK
        int courier_id FK
        string base_url
        text _api_key
        text _api_secret
        text _username
        text _password
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    Shipper {
        int id PK
        string name
        text address
        string postal_code
        string city
        string country
        string phone
        string email
        datetime created_at
        datetime updated_at
    }
    
    Consignee {
        int id PK
        string name
        text address
        string city
        string postal_code
        string country
        string phone
        string email
        datetime created_at
        datetime updated_at
    }
    
    Shipment {
        int id PK
        int courier_id FK
        int shipment_type_id FK
        string courier_external_id UK
        string reference_number UK
        int shipper_id FK
        int route_id FK
        int consignee_id FK
        int height
        int width
        int length
        string dimension_unit
        decimal weight
        string weight_unit
        datetime created_at
        datetime updated_at
    }
    
    ShipmentRequest {
        int id PK
        json request_body
        string reference_number
        string status
        text failed_reason
        int retries
        datetime last_retried_at
        datetime created_at
        datetime updated_at
    }
    
    ShipmentLabel {
        int id PK
        int shipment_id FK
        string reference_number
        string url
        string format
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    ShipmentStatus {
        int id PK
        int shipment_id FK
        string status
        string address
        string postal_code
        string country
        datetime created_at
        datetime updated_at
    }
    
    Courier ||--o{ CourierShipmentType : "supports"
    ShipmentType ||--o{ CourierShipmentType : "supported by"
    Courier ||--o{ CourierRoute : "serves"
    Route ||--o{ CourierRoute : "served by"
    Courier ||--|| CourierConfig : "configured with"
    Courier ||--o{ Shipment : "handles"
    ShipmentType ||--o{ Shipment : "categorized as"
    Shipper ||--o{ Shipment : "sends"
    Consignee ||--o{ Shipment : "receives"
    Route ||--o{ Shipment : "follows"
    Shipment ||--o{ ShipmentLabel : "has"
    Shipment ||--o{ ShipmentStatus : "tracks"
```

### Key Relationships

- **Courier ↔ ShipmentType**: Many-to-many relationship for supported shipment types
- **Courier ↔ Route**: Many-to-many relationship for supported routes
- **Courier ↔ CourierConfig**: One-to-one relationship for API credentials
- **Shipment**: Central entity linking courier, shipper, consignee, and route
- **ShipmentLabel**: One-to-many relationship for multiple label formats
- **ShipmentStatus**: One-to-many relationship for status history

## API Documentation

### Base URL
```
http://localhost:8000/api/shipment/
```

### Endpoints

#### 1. Create Shipment Request
```http
POST /shipment-requests/
```

**Request Body:**
```json
{
    "reference_number": "REF123456",
    "shipment_type_id": 1,
    "shipper": {
        "name": "John Doe",
        "address": "123 Main St",
        "city": "New York",
        "postal_code": "10001",
        "country": "USA",
        "phone": "+1234567890",
        "email": "john@example.com"
    },
    "consignee": {
        "name": "Jane Smith",
        "address": "456 Oak Ave",
        "city": "Los Angeles",
        "postal_code": "90210",
        "country": "USA",
        "phone": "+1987654321",
        "email": "jane@example.com"
    },
    "weight": 2.5,
    "weight_unit": "kg",
    "dimensions": {
        "height": 10,
        "width": 15,
        "length": 20
    },
    "dimension_unit": "cm",
    "pickup_date": "2024-01-15T10:00:00Z",
    "special_instructions": "Handle with care"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Shipment request created successfully",
    "data": {
        "request_id": 123,
        "reference_number": "REF123456",
        "status": "pending"
    }
}
```

#### 2. Get Shipment Label
```http
GET /shipment-labels/{reference_number}/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "reference_number": "REF123456",
        "labels": [
            {
                "url": "https://api.dhl.com/labels/ABC123.pdf",
                "format": "PDF",
                "is_active": true
            }
        ]
    }
}
```

#### 3. Track Shipment
```http
GET /shipments/{reference_number}/track/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "reference_number": "REF123456",
        "tracking_number": "DHL123456789",
        "current_status": "in_transit",
        "status_description": "Package is in transit",
        "events": [
            {
                "status": "picked_up",
                "description": "Package picked up",
                "timestamp": "2024-01-15T10:00:00Z",
                "location": "New York, NY, USA"
            },
            {
                "status": "in_transit",
                "description": "Package in transit",
                "timestamp": "2024-01-15T14:30:00Z",
                "location": "Chicago, IL, USA"
            }
        ]
    }
}
```

#### 4. Cancel Shipment
```http
POST /shipments/{reference_number}/cancel/
```

**Response:**
```json
{
    "success": true,
    "message": "Shipment cancelled successfully",
    "data": {
        "reference_number": "REF123456",
        "cancellation_id": "CANCEL123",
        "cancelled_at": "2024-01-15T16:00:00Z"
    }
}
```

#### 5. DHL Webhook
```http
POST /webhooks/dhl/
```

**Request Body:**
```json
{
    "shipment_id": "DHL123456789",
    "status": "delivered",
    "timestamp": "2024-01-16T09:00:00Z",
    "location": "Los Angeles, CA, USA"
}
```

## Key Features

### 1. Unified Courier Interface

All couriers implement the same interface, ensuring consistency:

```python
class CourierInterface(ABC):
    @abstractmethod
    def create_shipment(self, request: CourierRequest) -> CourierResponse:
        pass
    
    @abstractmethod
    def fetch_label(self, courier_external_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def track_shipment(self, courier_external_id: str) -> TrackingResponse:
        pass
```

### 2. Courier Factory Pattern

Dynamic courier instantiation with configuration management:

```python
class CourierFactory:
    def get_courier_instance(self, courier_name: str) -> CourierInterface:
        # Loads configuration from database
        # Returns configured courier instance
```

### 3. HTTP Retry Logic

Built-in retry mechanism with exponential backoff:

```python
class BaseHttpClient:
    def _make_request_with_retry(self, method, url, **kwargs):
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                if response.status_code < 500:
                    return response
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.backoff_factor ** attempt)
```

### 4. Status Mapping

Automatic mapping of courier-specific statuses to system statuses:

```python
class TrackingStatusMapper:
    COURIER_STATUS_MAPPING = {
        'dhl': {
            'PICKED_UP': {'status': 'picked_up', 'description': 'Package picked up'},
            'IN_TRANSIT': {'status': 'in_transit', 'description': 'Package in transit'},
            'DELIVERED': {'status': 'delivered', 'description': 'Package delivered'}
        }
    }
```

### 5. Encryption

Secure storage of sensitive courier credentials:

```python
class EncryptionManager:
    def encrypt(self, data: str) -> str:
        # AES encryption implementation
    
    def decrypt(self, encrypted_data: str) -> str:
        # AES decryption implementation
```

## Design Decisions

### 1. SOLID Principles

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Derived classes are substitutable for base classes
- **Interface Segregation**: Clients depend only on interfaces they use
- **Dependency Inversion**: Depend on abstractions, not concretions

### 2. Repository Pattern

Centralized data access with consistent interface:

```python
class BaseRepository:
    def get_by_id(self, id: int):
        pass
    
    def create(self, **kwargs):
        pass
    
    def update(self, id: int, **kwargs):
        pass
```

### 3. Factory Pattern

Dynamic courier instantiation without tight coupling:

```python
class CourierFactory:
    COURIER_CLASSES = {
        'dhl': DHLCourier,
        'aramex': AramexCourier,  # Future implementation
        'smsa': SMSACourier,      # Future implementation
    }
```

### 4. Strategy Pattern

Different algorithms for different couriers:

```python
class DHLPayloadBuilder:
    @staticmethod
    def build_dhl_payload(request: ShipmentRequest) -> Dict[str, Any]:
        # DHL-specific payload building logic
```

### 5. Observer Pattern

Webhook processing for real-time updates:

```python
class DHLWebhookProcessor:
    def process_webhook(self, webhook_data: Dict[str, Any]):
        # Process DHL webhook and update shipment status
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- Django 4.0+
- PostgreSQL 12+
- Redis (for background workers)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd couriers-unified
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Environment setup:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup:**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Seed data:**
```bash
python manage.py seed_all
```

7. **Run the application:**
```bash
python manage.py runserver
```

8. **Start background worker:**
```bash
./run_worker.sh
```

### Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/couriers_unified
REDIS_URL=redis://localhost:6379/0
ENCRYPTION_KEY=your-32-character-encryption-key
```

## Usage Examples

### Adding a New Courier

1. **Create courier class:**
```python
class AramexCourier(BaseCourier):
    def _create_http_client(self):
        return AramexHttpClient(self.config)
    
    def _prepare_payload(self, request: ShipmentRequest) -> Dict[str, Any]:
        return AramexPayloadBuilder.build_payload(request)
    
    def _map_response(self, response_data: Dict[str, Any]) -> ShipmentResponse:
        return AramexResponseMapper.map_response(response_data)
```

2. **Register in factory:**
```python
class CourierFactory:
    COURIER_CLASSES = {
        'dhl': DHLCourier,
        'aramex': AramexCourier,  # Add new courier
    }
```

3. **Add configuration:**
```python
# Use Django admin or management command
CourierConfig.objects.create(
    courier=courier,
    base_url='https://api.aramex.com',
    api_key='your-api-key',
    # ... other config
)
```

### Custom Status Mapping

```python
class TrackingStatusMapper:
    COURIER_STATUS_MAPPING = {
        'aramex': {
            'PICKUP': {'status': 'picked_up', 'description': 'Package picked up'},
            'IN_TRANSIT': {'status': 'in_transit', 'description': 'Package in transit'},
            'DELIVERED': {'status': 'delivered', 'description': 'Package delivered'},
        }
    }
```

## Sequence Diagrams

### Shipment Creation Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant RequestService
    participant CourierFactory
    participant DHLCourier
    participant DHLAPI
    participant Database
    participant Worker

    Client->>API: POST /shipment-requests/
    API->>RequestService: create_shipment_request()
    RequestService->>Database: Check existing request
    Database-->>RequestService: Request status
    
    alt New Request
        RequestService->>Database: Create shipment request
        RequestService-->>API: Return request ID
        API-->>Client: 201 Created
        
        RequestService->>Worker: Queue for processing
        Worker->>CourierFactory: get_courier_instance('dhl')
        CourierFactory->>Database: Load DHL config
        CourierFactory-->>Worker: DHL courier instance
        
        Worker->>DHLCourier: create_shipment(request)
        DHLCourier->>DHLAPI: POST /shipments
        DHLAPI-->>DHLCourier: Shipment response
        DHLCourier->>Database: Persist shipment
        DHLCourier-->>Worker: Success response
    else Existing Request
        RequestService-->>API: Return existing request
        API-->>Client: 200 OK
    end
```

### Label Fetching Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant LabelService
    participant CourierFactory
    participant DHLCourier
    participant DHLAPI
    participant Database

    Client->>API: GET /shipment-labels/{ref}/
    API->>LabelService: get_shipment_label_by_reference()
    LabelService->>Database: Get shipment by reference
    Database-->>LabelService: Shipment data
    
    alt Label exists in cache
        LabelService-->>API: Return cached label
        API-->>Client: 200 OK
    else Fetch from courier
        LabelService->>CourierFactory: get_courier_instance('dhl')
        CourierFactory-->>LabelService: DHL courier instance
        LabelService->>DHLCourier: fetch_label(courier_id)
        DHLCourier->>DHLAPI: GET /labels/{id}
        DHLAPI-->>DHLCourier: Label data
        DHLCourier->>Database: Store label
        DHLCourier-->>LabelService: Label response
        LabelService-->>API: Return label data
        API-->>Client: 200 OK
    end
```

### Tracking Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant TrackingService
    participant CourierFactory
    participant DHLCourier
    participant DHLAPI
    participant Database

    Client->>API: GET /shipments/{ref}/track/
    API->>TrackingService: track_shipment_by_reference()
    TrackingService->>Database: Get shipment by reference
    Database-->>TrackingService: Shipment data
    
    TrackingService->>CourierFactory: get_courier_instance('dhl')
    CourierFactory-->>TrackingService: DHL courier instance
    TrackingService->>DHLCourier: track_shipment(courier_id)
    DHLCourier->>DHLAPI: GET /tracking/{id}
    DHLAPI-->>DHLCourier: Tracking data
    DHLCourier->>Database: Update shipment status
    DHLCourier-->>TrackingService: Tracking response
    TrackingService-->>API: Return tracking data
    API-->>Client: 200 OK
```

### Webhook Processing Flow

```mermaid
sequenceDiagram
    participant DHL
    participant WebhookAPI
    participant WebhookProcessor
    participant Database
    participant NotificationService

    DHL->>WebhookAPI: POST /webhooks/dhl/
    WebhookAPI->>WebhookProcessor: process_webhook()
    WebhookProcessor->>WebhookProcessor: Validate webhook signature
    WebhookProcessor->>Database: Find shipment by courier_id
    Database-->>WebhookProcessor: Shipment data
    
    WebhookProcessor->>Database: Create/update shipment status
    WebhookProcessor->>NotificationService: Send status update
    NotificationService-->>WebhookProcessor: Notification sent
    WebhookProcessor-->>WebhookAPI: 200 OK
    WebhookAPI-->>DHL: 200 OK
```

## Contributing

### Adding New Couriers

1. Create courier-specific classes in `services/couriers/`
2. Implement HTTP client in `services/http_clients/`
3. Add payload builders and response mappers in `services/mapping/`
4. Register courier in `CourierFactory`
5. Add status mappings in `TrackingStatusMapper`
6. Create webhook processor if needed

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Add unit tests for new features
- Update documentation

### Testing

```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test shipment.tests.test_dhl_courier

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.
