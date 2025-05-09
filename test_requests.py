import requests
import unittest

BASE_URL = "http://127.0.0.1:5000"
TEST_USER = {
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
}

class TestAuthAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Clean up test user if exists
        requests.post(f"{BASE_URL}/register", json=TEST_USER)
    
    def test_1_register(self):
        # Test successful registration
        response = requests.post(f"{BASE_URL}/register", json=TEST_USER)
        self.assertEqual(response.status_code, 400)  # Already exists
        
        # Test missing fields
        response = requests.post(f"{BASE_URL}/register", json={"username": "test"})
        self.assertEqual(response.status_code, 400)
    
    def test_2_login(self):
        # Test successful login
        response = requests.post(f"{BASE_URL}/login", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.token = response.json()["access_token"]
        
        # Test invalid credentials
        response = requests.post(f"{BASE_URL}/login", json={
            "username": TEST_USER["username"],
            "password": "wrongpass"
        })
        self.assertEqual(response.status_code, 401)
    
    def test_3_protected_routes(self):
        # Test protected route without token
        response = requests.get(f"{BASE_URL}/protected")
        self.assertEqual(response.status_code, 401)
        
        # Test protected route with token
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/protected", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Protected route accessed successfully")
        
        # Test user info route
        response = requests.get(f"{BASE_URL}/user-info", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], TEST_USER["username"])

if __name__ == '__main__':
    unittest.main()