# Courier-Specific Mapping Services

## Problem with Original StatusMappingService

The original `StatusMappingService` violated the Single Responsibility Principle by handling multiple concerns:

1. **Status Mapping**: DHL status → Standard status
2. **Product Type Mapping**: DHL product codes ↔ Standard shipment types  
3. **Response Mapping**: DHL response → ShipmentResponse
4. **Payload Building**: Request → DHL payload structure

## New Architecture - Courier-Specific Organization

### Directory Structure
```
app/shipment/services/mapping/
├── __init__.py
├── README.md
├── base_mapper.py              # Abstract base classes
├── mapping_factory.py          # Factory for accessing courier mappers
└── dhl/                        # DHL-specific implementations
    ├── __init__.py
    ├── dhl_status_mapper.py
    ├── dhl_product_mapper.py
    ├── dhl_response_mapper.py
    └── dhl_payload_builder.py
```

### 1. DHL Status Mapper (`dhl/dhl_status_mapper.py`)
**Responsibility**: Maps DHL-specific statuses to standardized formats
- `map_dhl_status()`: Maps DHL status to standard status
- `get_supported_statuses()`: Lists supported DHL statuses

### 2. DHL Product Mapper (`dhl/dhl_product_mapper.py`)
**Responsibility**: Maps DHL-specific product types to standardized shipment types
- `map_dhl_product_type()`: Maps DHL product code to standard type
- `map_shipment_type_to_dhl_product()`: Maps standard type to DHL product code
- `get_supported_products()`: Lists supported DHL product codes

### 3. DHL Response Mapper (`dhl/dhl_response_mapper.py`)
**Responsibility**: Maps DHL-specific API responses to standardized ShipmentResponse
- `map_dhl_response_to_shipment_response()`: Maps DHL response to ShipmentResponse
- `extract_tracking_number()`: Extracts tracking number from DHL response
- `extract_courier_reference()`: Extracts courier reference from DHL response

### 4. DHL Payload Builder (`dhl/dhl_payload_builder.py`)
**Responsibility**: Builds DHL-specific API payloads from standardized requests
- `build_dhl_payload()`: Builds DHL payload from ShipmentRequest
- `build_dhl_tracking_payload()`: Builds DHL tracking payload
- `validate_dhl_payload()`: Validates DHL payload structure

### 5. Mapping Factory (`mapping_factory.py`)
**Responsibility**: Provides easy access to courier-specific mappers
- `get_status_mapper(courier)`: Get status mapper for specific courier
- `get_product_mapper(courier)`: Get product mapper for specific courier
- `get_response_mapper(courier)`: Get response mapper for specific courier
- `get_payload_builder(courier)`: Get payload builder for specific courier
- `register_courier()`: Register new courier mappers

## Benefits

1. **Single Responsibility**: Each service has one clear purpose
2. **Easier Testing**: Each service can be tested independently
3. **Better Maintainability**: Changes to one concern don't affect others
4. **Extensibility**: Easy to add new couriers by implementing new methods
5. **Reusability**: Services can be used independently across the application

## Usage

### Direct DHL Mapper Usage
```python
# DHL Status mapping
from .mapping.dhl.dhl_status_mapper import DHLStatusMapper
status = DHLStatusMapper.map_dhl_status('OK')  # Returns 'completed'

# DHL Product mapping
from .mapping.dhl.dhl_product_mapper import DHLProductMapper
product_code = DHLProductMapper.map_shipment_type_to_dhl_product('NORMAL')  # Returns 'V01PAK'

# DHL Response mapping
from .mapping.dhl.dhl_response_mapper import DHLResponseMapper
response = DHLResponseMapper.map_dhl_response_to_shipment_response(dhl_data, True)

# DHL Payload building
from .mapping.dhl.dhl_payload_builder import DHLPayloadBuilder
payload = DHLPayloadBuilder.build_dhl_payload(shipment_request)
```

### Using Mapping Factory (Recommended)
```python
# Using the factory for cleaner code
from .mapping.mapping_factory import mapping_factory

# Get DHL mappers
status_mapper = mapping_factory.get_status_mapper('dhl')
product_mapper = mapping_factory.get_product_mapper('dhl')
response_mapper = mapping_factory.get_response_mapper('dhl')
payload_builder = mapping_factory.get_payload_builder('dhl')

# Use the mappers
status = status_mapper.map_status('OK')
product_code = product_mapper.map_shipment_type_to_courier_product('NORMAL')
response = response_mapper.map_response(dhl_data, True)
payload = payload_builder.build_payload(shipment_request)
```

### Adding New Couriers
```python
# Register a new courier (e.g., FedEx)
from .mapping.mapping_factory import mapping_factory
from .fedex.fedex_status_mapper import FedExStatusMapper
from .fedex.fedex_product_mapper import FedExProductMapper
# ... other FedEx mappers

mapping_factory.register_courier(
    'fedex',
    status_mapper=FedExStatusMapper,
    product_mapper=FedExProductMapper,
    # ... other mappers
)
```

## Migration

The old `StatusMappingService` has been **completely removed** and all references have been updated to use the new separated services. The refactoring is complete and the system is fully functional with the new architecture.
