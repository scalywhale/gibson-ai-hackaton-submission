import sys
import os
import uuid
import unittest
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

class TestDatabase(unittest.TestCase):
    """Test the database operations"""
    
    def setUp(self):
        """Set up the test environment"""
        self.db = Database()
        self.test_username = f"test_user_{uuid.uuid4().hex[:8]}"
        self.test_password = "securepassword123"
        
    def test_create_and_get_user(self):
        """Test creating a user and retrieving it"""
        # Create a test user
        user_uuid = self.db.create_user(self.test_username, self.test_password)
        self.assertIsNotNone(user_uuid)
        
        # Get user by username
        user = self.db.get_user_by_username(self.test_username)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], self.test_username)
        self.assertEqual(user['password'], self.test_password)
        
        # Get user by UUID
        user = self.db.get_user_by_uuid(user_uuid)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], self.test_username)
        
        print("User create and get tests passed!")
        return user_uuid
        
    def test_create_and_get_goal(self):
        """Test creating a goal and retrieving it"""
        # First create a test user
        user_uuid = self.test_create_and_get_user()
        
        # Create a test goal
        goal_title = "Test Goal"
        goal_desc = "This is a test goal"
        current_year = datetime.now().year
        
        goal_uuid = self.db.create_goal(user_uuid, goal_title, goal_desc, current_year)
        self.assertIsNotNone(goal_uuid)
        
        # Get goal by UUID
        goal = self.db.get_goal_by_uuid(goal_uuid)
        self.assertIsNotNone(goal)
        self.assertEqual(goal['title'], goal_title)
        self.assertEqual(goal['description'], goal_desc)
        self.assertEqual(goal['year'], current_year)
        
        # Get goals for user
        goals = self.db.get_goals_by_user_uuid(user_uuid)
        self.assertGreater(len(goals), 0)
        
        print("Goal create and get tests passed!")
        return goal_uuid
        
    def test_create_and_get_monthly_breakdown(self):
        """Test creating a monthly breakdown and retrieving it"""
        # First create a test goal
        goal_uuid = self.test_create_and_get_goal()
        
        # Create test monthly breakdowns for first 3 months
        breakdown_uuids = []
        for month in range(1, 4):
            desc = f"Test milestone for month {month}"
            breakdown_uuid = self.db.create_monthly_breakdown(goal_uuid, month, desc)
            self.assertIsNotNone(breakdown_uuid)
            breakdown_uuids.append(breakdown_uuid)
            
        # Get breakdowns for goal
        breakdowns = self.db.get_monthly_breakdowns(goal_uuid)
        self.assertEqual(len(breakdowns), 3)
        
        # Update status of one breakdown
        self.db.update_monthly_breakdown(breakdown_uuids[0], status="ahead")
        
        # Get specific breakdown
        breakdown = self.db.get_monthly_breakdown_by_uuid(breakdown_uuids[0])
        self.assertEqual(breakdown['status'], "ahead")
        
        print("Monthly breakdown create, get, and update tests passed!")
        return breakdown_uuids[0]
        
    def test_create_and_get_feedback(self):
        """Test creating feedback and retrieving it"""
        # First create a test goal
        goal_uuid = self.test_create_and_get_goal()
        
        # Create test feedback
        feedback_text = "This is test feedback for the goal"
        feedback_type = "affirm"
        
        feedback_uuid = self.db.create_feedback(goal_uuid, feedback_text, feedback_type)
        self.assertIsNotNone(feedback_uuid)
        
        # Get feedback for goal
        feedback_list = self.db.get_feedback_for_goal(goal_uuid)
        self.assertGreater(len(feedback_list), 0)
        self.assertEqual(feedback_list[0]['feedback_text'], feedback_text)
        self.assertEqual(feedback_list[0]['feedback_type'], feedback_type)
        
        print("Feedback create and get tests passed!")

if __name__ == "__main__":
    unittest.main()
