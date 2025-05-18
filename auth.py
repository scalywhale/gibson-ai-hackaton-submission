import bcrypt
import uuid
from database import Database

class Auth:
    def __init__(self):
        self.db = Database()
        
    def hash_password(self, password):
        """Hash a password using bcrypt"""
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """Verify a password against a hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def register_user(self, username, password):
        """Register a new user"""
        # Check if user already exists
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            return False, "Username already exists"
        
        # Hash the password and create the user
        hashed_password = self.hash_password(password)
        try:
            user_uuid = self.db.create_user(username, hashed_password)
            return True, user_uuid
        except Exception as e:
            return False, str(e)
    
    def login_user(self, username, password):
        """Authenticate a user"""
        user = self.db.get_user_by_username(username)
        if not user:
            return False, "User not found"
        
        if self.verify_password(password, user['password']):
            return True, user['uuid']
        else:
            return False, "Incorrect password"
