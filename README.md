couriers-unified/
├── 📁 app/                                    # Main Django application
│   ├── 📄 manage.py                          # Django management script
│   ├── 📁 app/                               # Django project settings
│   │   ├── 📄 __init__.py
│   │   ├── 📄 settings.py                   # Main settings configuration
│   │   ├── 📄 urls.py                       # Root URL configuration
│   │   ├── 📄 wsgi.py                       # WSGI configuration
│   │   └── 📄 asgi.py                       # ASGI configuration
│   │
│   ├── 📁 core/                              # Core business logic
│   │   ├── 📄 __init__.py
│   │   ├── 📄 models.py                     # Core models (Courier, Routes, etc.)
│   │   ├── 📄 admin.py                      # Django admin configuration
│   │   ├── 📄 apps.py                       # App configuration
│   │   │
│   │   ├── 📁 migrations/                   # Database migrations
│   │   │   ├── 📄 0001_create_couriers_table.py
│   │   │   ├── 📄 0002_create_shipment_types_table.py
│   │   │   ├── 📄 0003_create_courier_shipment_types_table.py
│   │   │   ├── 📄 0004_create_routes_table.py
│   │   │   ├── 📄 0005_create_courier_routes_table.py
│   │   │   └── 📄 0006_create_courier_configs_table.py
│   │   │
│   │   ├── 📁 repositories/                  # Data access layer
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 courier_repository.py
│   │   │
│   │   ├── 📁 utils/                         # Utility functions
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 encryption.py             # Encryption utilities
│   │   │
│   │   └── 📁 management/commands/           # Django management commands
│   │       ├── 📄 __init__.py
│   │       ├── 📄 seed_all.py
│   │       ├── 📄 seed_courier_config.py
│   │       ├── 📄 seed_courier_data.py
│   │       └── 📄 wait_for_db.py
│   │
│   └── 📁 shipment/                          # Shipment management app
│       ├── 📄 __init__.py
│       ├── 📄 models.py                     # Shipment-related models
│       ├── 📄 admin.py                      # Admin configuration
│       ├── 📄 apps.py                       # App configuration
│       ├── 📄 serializers.py                # DRF serializers
│       ├── 📄 views.py                      # Main API views
│       ├── 📄 urls.py                       # URL routing
│       ├── 📄 webhook_views.py              # Webhook endpoints
│       ├── 📄 tests.py                      # Test cases
│       │
│       ├── 📁 migrations/                   # Database migrations
│       │   ├── 📄 0001_create_shippers_table.py
│       │   ├── 📄 0002_create_consignees_table.py
│       │   ├── 📄 0003_create_shipment_requests_table.py
│       │   ├── 📄 0004_create_shipments_table.py
│       │   ├── 📄 0005_alter_weight_field_to_decimal.py
│       │   ├── 📄 0006_create_shipment_labels_table.py
│       │   └── 📄 0007_create_shipment_statuses_table.py
│       │
│       ├── 📁 schemas/                       # Data transfer objects
│       │   ├── 📄 __init__.py
│       │   ├── 📄 cancellation_response.py  # Cancellation response schema
│       │   ├── 📄 label_response.py         # Label response schema
│       │   ├── 📄 shipment_request.py       # Shipment request schema
│       │   ├── 📄 shipment_request_response.py
│       │   ├── 📄 shipment_response.py      # Shipment response schema
│       │   └── 📄 tracking_response.py      # Tracking response schema
│       │
│       ├── 📁 repositories/                  # Data access layer
│       │   ├── 📄 __init__.py
│       │   ├── 📄 base_repository.py        # Base repository class
│       │   ├── 📄 repository_factory.py     # Repository factory
│       │   ├── 📄 shipment_label_repository.py
│       │   ├── 📄 shipment_repository.py
│       │   ├── 📄 shipment_request_repository.py
│       │   └── 📄 shipper_consignee_repository.py
│       │
│       ├── 📁 services/                      # Business logic layer
│       │   ├── 📄 __init__.py
│       │   │
│       │   ├── 📁 cancellation/             # Cancellation services
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 courier_cancellation_service.py    # Courier-specific cancellation
│       │   │   └── 📄 shipment_cancellation_service.py    # Main cancellation orchestration
│       │   │
│       │   ├── 📁 couriers/                 # Courier implementations
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 base_courier.py       # Base courier class
│       │   │   ├── 📄 cancellable_courier_interface.py    # Cancellation interface
│       │   │   ├── 📄 courier_factory.py    # Courier factory pattern
│       │   │   ├── 📄 courier_interface.py  # Main courier interface
│       │   │   ├── 📄 courier_processor.py  # Courier processing logic
│       │   │   ├── 📄 dhl_courier.py        # DHL implementation
│       │   │   └── 📄 find_available_courier.py
│       │   │
│       │   ├── 📁 http_clients/             # HTTP client implementations
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 base_client.py        # Base HTTP client
│       │   │   └── 📄 dhl_client.py         # DHL HTTP client
│       │   │
│       │   ├── 📁 labels/                   # Label management
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 dhl_label_response_parser.py
│       │   │   ├── 📄 label_cache_service.py
│       │   │   ├── 📄 label_response_handler.py
│       │   │   └── 📄 shipment_label_service.py
│       │   │
│       │   ├── 📁 mapping/                  # Data mapping services
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 status_mapping_service.py    # Status mapping logic
│       │   │   └── 📁 dhl/                  # DHL-specific mappings
│       │   │       ├── 📄 __init__.py
│       │   │       ├── 📄 dhl_payload_builder.py
│       │   │       ├── 📄 dhl_product_mapper.py
│       │   │       ├── 📄 dhl_response_mapper.py
│       │   │       └── 📄 dhl_status_mapper.py
│       │   │
│       │   ├── 📁 requests/                 # Request processing
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 request_batch_processor.py
│       │   │   ├── 📄 request_data_converter.py
│       │   │   ├── 📄 request_processor.py
│       │   │   └── 📄 shipment_request_service.py
│       │   │
│       │   ├── 📁 shipments/                # Shipment management
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 request_status_manager.py
│       │   │   ├── 📄 shipment_creation_service.py
│       │   │   ├── 📄 shipment_lookup_service.py
│       │   │   └── 📄 shipment_processor.py
│       │   │
│       │   ├── 📁 status/                   # Status management
│       │   │   └── 📄 shipment_status_service.py
│       │   │
│       │   ├── 📁 tracking/                 # Tracking services
│       │   │   ├── 📄 __init__.py
│       │   │   ├── 📄 dhl_tracking_response_parser.py
│       │   │   ├── 📄 shipment_tracking_service.py
│       │   │   ├── 📄 tracking_response_handler.py
│       │   │   └── 📄 tracking_status_mapper.py
│       │   │
│       │   └── 📁 webhooks/                 # Webhook processing
│       │       ├── 📄 __init__.py
│       │       ├── 📄 dhl_webhook_parser.py      # DHL webhook parser
│       │       ├── 📄 dhl_webhook_processor.py   # Webhook processor
│       │       └── 📄 dhl_webhook_validator.py   # Webhook validator
│       │
│       ├── 📁 management/commands/          # Django management commands
│       │   ├── 📄 __init__.py
│       │   └── 📄 shipment_worker.py
│       │
│       └── 📁 views/                        # Additional view modules
│           └─
