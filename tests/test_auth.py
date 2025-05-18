import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import Auth

class TestAuth(unittest.TestCase):
    """Test the authentication functionality"""
    
    def setUp(self):
        """Set up the test environment"""
        self.auth = Auth()
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        # Test plain password
        password = "securepassword123"
        
        # Hash the password
        hashed = self.auth.hash_password(password)
        self.assertNotEqual(password, hashed)
        
        # Verify the password against the hash
        self.assertTrue(self.auth.verify_password(password, hashed))
        
        # Test with incorrect password
        wrong_password = "wrongpassword"
        self.assertFalse(self.auth.verify_password(wrong_password, hashed))
        
        print("Password hashing and verification tests passed!")
    
    @patch('auth.Auth.hash_password')
    @patch('database.Database.create_user')
    @patch('database.Database.get_user_by_username')
    def test_register_user(self, mock_get_user, mock_create_user, mock_hash_password):
        """Test user registration"""
        # Mock the dependencies
        mock_get_user.return_value = None  # No existing user
        mock_hash_password.return_value = "hashed_password"
        mock_create_user.return_value = "test_uuid"
        
        # Test successful registration
        success, result = self.auth.register_user("testuser", "password123")
        self.assertTrue(success)
        self.assertEqual(result, "test_uuid")
        
        # Mock existing user
        mock_get_user.return_value = {"username": "testuser"}
        
        # Test registration with existing username
        success, result = self.auth.register_user("testuser", "password123")
        self.assertFalse(success)
        self.assertEqual(result, "Username already exists")
        
        print("User registration tests passed!")
    
    @patch('auth.Auth.verify_password')
    @patch('database.Database.get_user_by_username')
    def test_login_user(self, mock_get_user, mock_verify_password):
        """Test user login"""
        # Mock the dependencies
        mock_get_user.return_value = {
            "username": "testuser",
            "password": "hashed_password",
            "uuid": "test_uuid"
        }
        mock_verify_password.return_value = True
        
        # Test successful login
        success, result = self.auth.login_user("testuser", "password123")
        self.assertTrue(success)
        self.assertEqual(result, "test_uuid")
        
        # Test login with incorrect password
        mock_verify_password.return_value = False
        success, result = self.auth.login_user("testuser", "wrongpassword")
        self.assertFalse(success)
        self.assertEqual(result, "Incorrect password")
        
        # Test login with non-existent user
        mock_get_user.return_value = None
        success, result = self.auth.login_user("nonexistent", "password123")
        self.assertFalse(success)
        self.assertEqual(result, "User not found")
        
        print("User login tests passed!")

if __name__ == "__main__":
    unittest.main()
