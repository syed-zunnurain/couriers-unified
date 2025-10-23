# Couriers Unified API

A unified shipping API that integrates with multiple courier services (currently DHL) to provide a single interface for creating shipments, tracking packages, printing labels, and handling cancellations. Built with Django REST Framework and designed for scalability and easy courier integration.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd couriers-unified
   ```

2. **Start the application with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   
3. **Start the Background Worker**
The system includes a background worker for processing shipment requests:
```bash
./run_worker.sh
```

4. **Access the application**
   - API Base URL: `http://localhost:8000`
   - Database: PostgreSQL on port `5433`

The application will automatically:
- Set up the PostgreSQL database
- Run database migrations
- Seed initial data (couriers, routes, shipment types)
- Start the Django development server

### Database Credentials

**Development Database:**
- Host: `localhost` (or `db` from within Docker)
- Port: `5433`
- Database: `devdb`
- Username: `devuser`
- Password: `changeme`

**⚠️ Security Note:** In production, move these credentials to a `.env` file and update `settings.py` to use environment variables. The current setup is for development only.

## 🏗️ System Architecture

The system follows a modular, service-oriented architecture designed for easy courier integration and maintainability.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Application]
        B[Mobile App]
        C[Third-party Integration]
    end
    
    subgraph "API Layer"
        D[Django REST API]
        E[Authentication]
        F[Request Validation]
    end
    
    subgraph "Service Layer"
        G[Shipment Request Service]
        H[Courier Factory]
        I[Label Service]
        J[Tracking Service]
        K[Cancellation Service]
        L[Webhook Processor]
    end
    
    subgraph "Courier Layer"
        M[DHL Courier]
        N[Future Courier 1]
        O[Future Courier 2]
    end
    
    subgraph "Data Layer"
        P[PostgreSQL Database]
        Q[Repository Pattern]
    end
    
    subgraph "External Services"
        R[DHL API]
        S[Other Courier APIs]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    D --> F
    D --> G
    G --> H
    H --> M
    H --> N
    H --> O
    M --> R
    N --> S
    O --> S
    G --> Q
    Q --> P
    I --> H
    J --> H
    K --> H
    L --> G
```

### Key Components

- **API Layer**: Django REST Framework endpoints for all operations
- **Service Layer**: Business logic and orchestration
- **Courier Layer**: Pluggable courier implementations
- **Repository Layer**: Data access abstraction
- **Webhook Processing**: Real-time status updates from couriers

## 🗄️ Database Schema (ERD)

```mermaid
erDiagram
    COURIERS {
        int id PK
        string name UK
        boolean supports_cancellation
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    SHIPMENT_TYPES {
        int id PK
        string name UK
        datetime created_at
        datetime updated_at
    }
    
    ROUTES {
        int id PK
        string origin
        string destination
        datetime created_at
        datetime updated_at
    }
    
    COURIER_SHIPMENT_TYPES {
        int id PK
        int courier_id FK
        int shipment_type_id FK
        datetime created_at
        datetime updated_at
    }
    
    COURIER_ROUTES {
        int id PK
        int courier_id FK
        int route_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    COURIER_CONFIGS {
        int id PK
        int courier_id FK
        string base_url
        text api_key_encrypted
        text api_secret_encrypted
        text username_encrypted
        text password_encrypted
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    SHIPPERS {
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
    
    CONSIGNEES {
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
    
    SHIPMENTS {
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
    
    SHIPMENT_REQUESTS {
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
    
    SHIPMENT_LABELS {
        int id PK
        int shipment_id FK
        string reference_number
        string url
        string format
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    SHIPMENT_STATUSES {
        int id PK
        int shipment_id FK
        string status
        string address
        string postal_code
        string country
        datetime created_at
        datetime updated_at
    }
    
    COURIERS ||--o{ COURIER_SHIPMENT_TYPES : supports
    SHIPMENT_TYPES ||--o{ COURIER_SHIPMENT_TYPES : supported_by
    COURIERS ||--o{ COURIER_ROUTES : serves
    ROUTES ||--o{ COURIER_ROUTES : served_by
    COURIERS ||--|| COURIER_CONFIGS : configured_with
    COURIERS ||--o{ SHIPMENTS : handles
    SHIPMENT_TYPES ||--o{ SHIPMENTS : categorized_as
    ROUTES ||--o{ SHIPMENTS : follows
    SHIPPERS ||--o{ SHIPMENTS : sends
    CONSIGNEES ||--o{ SHIPMENTS : receives
    SHIPMENTS ||--o{ SHIPMENT_LABELS : has
    SHIPMENTS ||--o{ SHIPMENT_STATUSES : tracked_by
```

## 🔄 API Sequence Diagrams

### 1. Create Shipment

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant RequestService
    participant CourierFactory
    participant DHLCourier
    participant DHLAPI
    participant Database
    
    Client->>API: POST /shipment-requests/
    API->>API: Validate request data
    API->>RequestService: create_shipment_request()
    RequestService->>RequestService: Find available courier
    RequestService->>CourierFactory: get_courier_instance()
    CourierFactory->>Database: Get courier config
    Database-->>CourierFactory: Return config
    CourierFactory-->>RequestService: Return DHL instance
    RequestService->>DHLCourier: create_shipment()
    DHLCourier->>DHLCourier: Prepare DHL payload
    DHLCourier->>DHLAPI: POST /shipments
    DHLAPI-->>DHLCourier: Return shipment response
    DHLCourier->>DHLCourier: Map response
    DHLCourier->>Database: Persist shipment
    Database-->>DHLCourier: Confirm persistence
    DHLCourier-->>RequestService: Return shipment response
    RequestService-->>API: Return result
    API-->>Client: Return shipment created response
```

### 2. Print Label

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant LabelService
    participant CourierFactory
    participant DHLCourier
    participant DHLAPI
    participant Database
    
    Client->>API: GET /shipment-labels/{reference_number}/
    API->>LabelService: get_shipment_label_by_reference()
    LabelService->>Database: Find shipment by reference
    Database-->>LabelService: Return shipment
    LabelService->>CourierFactory: fetch_label()
    CourierFactory->>DHLCourier: fetch_label()
    DHLCourier->>DHLAPI: GET /labels/{tracking_number}
    DHLAPI-->>DHLCourier: Return label data
    DHLCourier->>DHLCourier: Parse label response
    DHLCourier-->>CourierFactory: Return label data
    CourierFactory-->>LabelService: Return label data
    LabelService->>Database: Save label info
    Database-->>LabelService: Confirm save
    LabelService-->>API: Return label response
    API-->>Client: Return label URL and details
```

### 3. Track Shipment

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant TrackingService
    participant CourierFactory
    participant DHLCourier
    participant DHLAPI
    participant Database
    
    Client->>API: GET /shipments/{reference_number}/track/
    API->>TrackingService: track_shipment_by_reference()
    TrackingService->>Database: Find shipment by reference
    Database-->>TrackingService: Return shipment
    TrackingService->>CourierFactory: track_shipment()
    CourierFactory->>DHLCourier: track_shipment()
    DHLCourier->>DHLAPI: GET /tracking/{tracking_number}
    DHLAPI-->>DHLCourier: Return tracking data
    DHLCourier->>DHLCourier: Parse and map status
    DHLCourier-->>CourierFactory: Return tracking response
    CourierFactory-->>TrackingService: Return tracking response
    TrackingService-->>API: Return tracking data
    API-->>Client: Return tracking information
```

### 4. Status Webhook

```mermaid
sequenceDiagram
    participant DHL
    participant API
    participant WebhookValidator
    participant WebhookParser
    participant WebhookProcessor
    participant Database
    
    DHL->>API: POST /webhooks/dhl/
    API->>WebhookValidator: validate_request()
    WebhookValidator-->>API: Validation result
    API->>WebhookParser: parse(payload)
    WebhookParser-->>API: Parsed webhook data
    API->>WebhookProcessor: process_webhook()
    WebhookProcessor->>Database: Find shipment by tracking number
    Database-->>WebhookProcessor: Return shipment
    WebhookProcessor->>WebhookProcessor: Map status
    WebhookProcessor->>Database: Save status update
    Database-->>WebhookProcessor: Confirm save
    WebhookProcessor-->>API: Processing result
    API-->>DHL: Return webhook acknowledgment
```

### 5. Cancel Shipment

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant CancellationService
    participant CourierFactory
    participant DHLCourier
    participant DHLAPI
    participant Database
    
    Client->>API: POST /shipments/{reference_number}/cancel/
    API->>CancellationService: cancel_shipment_by_reference()
    CancellationService->>Database: Find shipment by reference
    Database-->>CancellationService: Return shipment
    CancellationService->>CancellationService: Check if cancellable
    CancellationService->>CourierFactory: cancel_shipment()
    CourierFactory->>DHLCourier: cancel_shipment()
    DHLCourier->>DHLAPI: POST /shipments/{id}/cancel
    DHLAPI-->>DHLCourier: Return cancellation result
    DHLCourier-->>CourierFactory: Return result
    CourierFactory-->>CancellationService: Return result
    CancellationService->>Database: Update shipment status
    Database-->>CancellationService: Confirm update
    CancellationService-->>API: Return cancellation result
    API-->>Client: Return cancellation response
```

## 📦 Shipment Types

Shipment types define the delivery speed and service level for your packages. Each courier supports different shipment types, and the system automatically maps these to the appropriate courier-specific product codes.

### Available Shipment Types

| ID | Name | Description | DHL Product Code | Supported by DHL |
|----|------|-------------|------------------|------------------|
| 1 | `NORMAL` | Standard delivery (1-3 business days) | `V01PAK` | ✅ |
| 2 | `URGENT` | Express delivery (1-2 business days) | `V53WPAK` | ✅ |
| 3 | `SAME_DAY_DELIVERY` | Same-day delivery | `V54EPAK` | ❌ |

### How Shipment Types Work

1. **Courier Compatibility**: Not all couriers support all shipment types. The system maintains a mapping table (`courier_shipment_types`) that defines which shipment types each courier can handle.

2. **Automatic Mapping**: When you create a shipment request, the system:
   - Validates that the requested courier supports the specified shipment type
   - Maps the internal shipment type to the courier's specific product code
   - Uses the appropriate courier API parameters

### Using Shipment Types in API Requests

When creating a shipment request, specify the `shipment_type_id` in your request:

```json
{
  "shipment_type_id": 1,  // Use ID 1 for NORMAL delivery
  "reference_number": "REF123456",
  // ... other fields
}
```

## 📚 API Documentation

### 1. Create Shipment Request

**Endpoint:** `POST /shipment-requests/`

**cURL Example:**
```bash
curl --location 'http://localhost:8000/api/v1/shipment-requests/' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
    "shipment_type_id": 2,
    "reference_number": "REF123437",
    "shipper": {
        "name": "John Doe",
        "address": "123 Main Street, Al Olaya",
        "city": "Berlin",
        "country": "DEU",
        "phone": "+966501234567",
        "email": "john.doe1@example.com",
        "postal_code": 12235
    },
    "consignee": {
        "name": "Jane Smith",
        "address": "456 King Abdulaziz Road",
        "city": "Bonn",
        "country": "DEU",
        "phone": "+966509876543",
        "email": "jane.smith1@example.com",
        "postal_code": 12345
    },
    "pickup_date": "2024-01-15",
    "weight": 1.2,
    "weight_unit": "kg",
    "dimensions": {
        "length": 50,
        "width": 30,
        "height": 20
    },
    "dimension_unit": "mm",
    "special_instructions": "Handle with care. Fragile items included."
}'
```

**Request Body Schema:**
```json
{
  "shipment_type_id": 2,
  "reference_number": "REF123437",
  "shipper": {
    "name": "John Doe",
    "address": "123 Main Street, Al Olaya",
    "city": "Berlin",
    "country": "DEU",
    "phone": "+966501234567",
    "email": "john.doe1@example.com",
    "postal_code": 12235
  },
  "consignee": {
    "name": "Jane Smith",
    "address": "456 King Abdulaziz Road",
    "city": "Bonn",
    "country": "DEU",
    "phone": "+966509876543",
    "email": "jane.smith1@example.com",
    "postal_code": 12345
  },
  "pickup_date": "2024-01-15",
  "weight": 1.2,
  "weight_unit": "kg",
  "dimensions": {
    "length": 50,
    "width": 30,
    "height": 20
  },
  "dimension_unit": "mm",
  "special_instructions": "Handle with care. Fragile items included."
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "Shipment request created successfully",
    "data": {
        "id": 1,
        "reference_number": "REF123437",
        "status": "pending",
        "created_at": "2025-10-21T20:24:07.444955+00:00",
        "shipper_id": 1,
        "consignee_id": 1
    }
}
```

### 2. Get Shipment Label

**Endpoint:** `GET /shipment-labels/{reference_number}`

**cURL Example:**
```bash
curl --location 'http://localhost:8000/api/v1/shipment-labels/REF123437'
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Label retrieved successfully",
    "data": {
        "id": 3,
        "reference_number": "REF123437",
        "url": "https://api-sandbox.dhl.com/parcel/de/shipping/v2/labels?token=x5xzrHE7ctmqPqk33k%2BKkKVOF7rDdlCe35HwWACAmA5yiaN4QeyVlJ2S%2FyRW1IQrbsqJ%2Bf%2FB4JuUWex0tKUE%2BOrgzoO6MrjST%2FOE69eW2sTHRtM0vUAgsEvI6lLukTpUO3NpawftZJ%2FeqEIwt8R1eh9E0HUyjNbAudun7tcX68jsnJ6p9%2FQD8AocXOJE0XcD",
        "format": "PDF",
        "is_active": true,
        "created_at": "2025-10-21T21:16:09.008546+00:00"
    }
}
```

### 3. Track Shipment

**Endpoint:** `GET /api/v1/shipments/{reference_number}/track`

**cURL Example:**
```bash
curl --location 'http://localhost:8000/api/v1/shipments/REF123437/track'
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Tracking information retrieved successfully",
    "data": {
        "service": "DHL",
        "current_status": "created",
        "status_description": "Created",
        "current_location": {
            "address": "123 Main Street, Al Olaya, Berlin",
            "country": "DEU",
            "postal_code": "12235"
        },
        "events": [
            {
                "timestamp": "2025-10-21T20:24:13.736251+00:00",
                "status": "created",
                "description": "Created",
                "location": {
                    "address": "123 Main Street, Al Olaya, Berlin",
                    "country": "DEU",
                    "postal_code": "12235"
                }
            }
        ],
        "origin": {
            "address": "123 Main Street, Al Olaya",
            "city": "Berlin",
            "country": "DEU",
            "postal_code": "12235"
        },
        "destination": {
            "address": "456 King Abdulaziz Road",
            "city": "Bonn",
            "country": "DEU",
            "postal_code": "12345"
        },
        "reference_number": "REF123437",
        "shipment_id": 5,
        "error": null,
        "error_code": null
    }
}
```

### 4. Cancel Shipment

**Endpoint:** `POST /api/v1/shipments/{reference_number}/cancel/`

**cURL Example:**
```bash
curl --location --request POST 'http://localhost:8000/api/v1/shipments/REF123437/cancel/'
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Shipment cancelled successfully",
    "data": {
        "shipment_id": 5,
        "reference_number": "REF123437",
        "cancelled_at": "2025-10-21T21:18:29.243064"
    }
}
```

### 5. DHL Webhook

**Endpoint:** `POST /api/v1/webhooks/dhl/`

**cURL Example:**
```bash
curl --location 'http://localhost:8000/api/v1/webhooks/dhl/' \
--header 'X-API-Key: dhl-webhook-secret-key-2024' \
--header 'Content-Type: application/json' \
--data '{
    "tracking_number": "0034043333301020017128697",
    "status": "in_transit",
    "location": {
        "countryCode": "DEU",
        "postalCode": "12345",
        "addressLocality": "456 King Abdulaziz Road"
    }
}'
```

**Headers:**
```
X-API-Key: dhl-webhook-secret-key-2024
Content-Type: application/json
```

**Request Body:**
```json
{
    "tracking_number": "0034043333301020017128697",
    "status": "in_transit",
    "location": {
        "countryCode": "DEU",
        "postalCode": "12345",
        "addressLocality": "456 King Abdulaziz Road"
    }
}
```

**Important Notes:**
- The `tracking_number` in the webhook payload is the **courier's tracking number** (e.g., DHL's tracking number)
- The system maps this to our internal shipment by searching the `shipments` table using the `courier_external_id` field
- This allows us to track status updates from couriers using their native tracking identifiers

**Success Response (200):**
```json
{
    "success": true,
    "message": "Webhook processed successfully",
    "data": {
        "shipment_id": 4,
        "reference_number": "REF123427",
        "status_entry_id": 13,
        "mapped_status": "in_transit"
    }
}
```

## 🔧 Adding a New Courier

The system is designed to easily integrate new courier services. Here's a simple step-by-step guide:

### 1. Database Setup
- Add courier to `Courier` table
- Create `CourierConfig` with API credentials
- Add supported routes and shipment types

### 2. Create HTTP Client
- Extend `BaseHttpClient` class
- Implement `create_shipment()`, `get_label()`, `track_shipment()` methods

### 3. Create Courier Class
- Extend `BaseCourier` class
- Implement `_prepare_payload()`, `_map_response()`, `fetch_label()`, `track_shipment()` methods

### 4. Create Mapping Services
- Build payload converter for courier API format
- Create response mapper to unified format
- Add status mapping if needed

### 5. Register Courier
- Add courier class to `CourierFactory.COURIER_CLASSES`
- Update status mapping service

### 6. Add Webhook Support (Optional)
- Create webhook parser
- Add webhook endpoint to URLs

### 7. Test Integration
- Test shipment creation, label fetching, and tracking
- Run test suite to ensure compatibility

## 🛠️ Development

### Running Tests
```bash
docker-compose exec app python manage.py test
```

### Running Background Worker
```bash
# Start the background worker using the shell script
sh worker.sh

### Database Migrations
```bash
docker-compose exec app python manage.py makemigrations
docker-compose exec app python manage.py migrate
```

### Seeding Data
```bash
docker-compose exec app python manage.py seed_all
```

## 📝 Environment Variables

### Current Setup (Development)
The application currently uses hardcoded values in `settings.py` for development convenience.

### Production Setup (Recommended)
For production deployment, create a `.env` file in the project root:

```bash
# .env file
DB_HOST=your-db-host
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASS=your-secure-password
DHL_WEBHOOK_API_KEY=your-dhl-webhook-key
SECRET_KEY=your-django-secret-key
ENCRYPTION_KEY=your-encryption-key
```

Then update `settings.py` to use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default')
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'default-key').encode()
DHL_WEBHOOK_API_KEY = os.environ.get('DHL_WEBHOOK_API_KEY', 'dhl-webhook-secret-key-2024')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST', 'db'),
        'NAME': os.environ.get('DB_NAME', 'devdb'),
        'USER': os.environ.get('DB_USER', 'devuser'),
        'PASSWORD': os.environ.get('DB_PASS', 'changeme'),
    }
}
```

### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | Database host | `db` | Yes |
| `DB_NAME` | Database name | `devdb` | Yes |
| `DB_USER` | Database user | `devuser` | Yes |
| `DB_PASS` | Database password | `changeme` | Yes |
| `DHL_WEBHOOK_API_KEY` | DHL webhook authentication key | `dhl-webhook-secret-key-2024` | Yes |
| `SECRET_KEY` | Django secret key | `django-insecure-default` | Yes |
| `ENCRYPTION_KEY` | Encryption key for sensitive data | `default-key` | Yes |
