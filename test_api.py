import requests
import json

# Test data for creating a shipment request
test_data = {
    "shipment_type_id": 1,  # NORMAL
    "route_id": 1,  # RUH → JED
    "reference_number": "REF123456",
    "shipper": {
        "name": "John Doe",
        "address": "123 Main Street, Al Olaya",
        "city": "Riyadh",
        "country": "Saudi Arabia",
        "phone": "+966501234567",
        "email": "john.doe@example.com"
    },
    "consignee": {
        "name": "Jane Smith",
        "address": "456 King Abdulaziz Road",
        "city": "Jeddah",
        "country": "Saudi Arabia",
        "phone": "+966509876543",
        "email": "jane.smith@example.com"
    },
    "items": [
        {
            "name": "Electronics",
            "quantity": 2,
            "description": "Laptop computers"
        },
        {
            "name": "Documents",
            "quantity": 1,
            "description": "Important business documents"
        }
    ],
    "pickup_date": "2024-01-15",
    "weight": 5.5,
    "dimensions": {
        "length": 50,
        "width": 30,
        "height": 20
    },
    "special_instructions": "Handle with care. Fragile items included."
}

# Test the API endpoint
url = "http://localhost:8000/api/shipment/shipment-requests/"
headers = {
    "Content-Type": "application/json"
}

def test_shipment_request(data, test_name):
    print(f"\n=== {test_name} ===")
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Django server is running.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test 1: Create new shipment request
print("Testing shipment request creation with duplicate reference number handling...")
result1 = test_shipment_request(test_data, "First Request (Should Create)")

# Test 2: Try to create another request with same reference number
print("\n" + "="*50)
test_data2 = test_data.copy()
test_data2["shipper"]["name"] = "Different Shipper"  # Different shipper but same reference
result2 = test_shipment_request(test_data2, "Second Request (Should Return Existing)")

# Test 3: Try with different reference number
print("\n" + "="*50)
test_data3 = test_data.copy()
test_data3["reference_number"] = "REF789012"
test_data3["shipper"]["name"] = "Another Shipper"
result3 = test_shipment_request(test_data3, "Third Request (Different Reference - Should Create)")
