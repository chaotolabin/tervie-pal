"""
Script test các endpoints Biometrics
Chạy: python test_biometrics.py (sau khi server đã chạy)
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1/biometrics"


def test_create_biometrics():
    """Test POST /biometrics"""
    print("\n=== TEST 1: Create Biometrics Log ===")
    
    payload = {
        "logged_at": datetime.now().isoformat(),
        "weight_kg": 75.5,
        "height_cm": 175.0
    }
    
    response = requests.post(BASE_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_list_biometrics():
    """Test GET /biometrics"""
    print("\n=== TEST 2: List Biometrics Logs ===")
    
    response = requests.get(f"{BASE_URL}?limit=10")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_get_latest():
    """Test GET /biometrics/latest"""
    print("\n=== TEST 3: Get Latest Biometrics ===")
    
    response = requests.get(f"{BASE_URL}/latest")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_update_biometrics(biometric_id: int):
    """Test PATCH /biometrics/{id}"""
    print(f"\n=== TEST 4: Update Biometrics {biometric_id} ===")
    
    payload = {
        "weight_kg": 76.0  # Chỉ update weight
    }
    
    response = requests.patch(f"{BASE_URL}/{biometric_id}", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_delete_biometrics(biometric_id: int):
    """Test DELETE /biometrics/{id}"""
    print(f"\n=== TEST 5: Delete Biometrics {biometric_id} ===")
    
    response = requests.delete(f"{BASE_URL}/{biometric_id}")
    print(f"Status: {response.status_code}")
    print("Response: No content (204)")


if __name__ == "__main__":
    print("🚀 Testing Biometrics Endpoints...")
    
    # Test create và lấy ID
    biometric_id = test_create_biometrics()
    
    # Test list
    test_list_biometrics()
    
    # Test latest
    test_get_latest()
    
    # Test update (nếu có ID)
    if biometric_id:
        test_update_biometrics(biometric_id)
    
    # Test delete (nếu có ID)
    # if biometric_id:
    #     test_delete_biometrics(biometric_id)
    
    print("\nAll tests completed!")