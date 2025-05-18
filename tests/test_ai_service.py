import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import AIService

class TestAIService(unittest.TestCase):
    """Test the AI service functionality"""
    
    def setUp(self):
        """Set up the test environment"""
        # Use a dummy API key for testing
        self.ai_service = AIService("test_api_key")
    
    @patch('openai.chat.completions.create')
    def test_generate_monthly_breakdowns(self, mock_create):
        """Test generating monthly breakdowns with AI"""
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        [
            {"month": 1, "description": "January milestone"},
            {"month": 2, "description": "February milestone"},
            {"month": 3, "description": "March milestone"},
            {"month": 4, "description": "April milestone"},
            {"month": 5, "description": "May milestone"},
            {"month": 6, "description": "June milestone"},
            {"month": 7, "description": "July milestone"},
            {"month": 8, "description": "August milestone"},
            {"month": 9, "description": "September milestone"},
            {"month": 10, "description": "October milestone"},
            {"month": 11, "description": "November milestone"},
            {"month": 12, "description": "December milestone"}
        ]
        '''
        mock_create.return_value = mock_response
        
        # Call the function
        breakdowns = self.ai_service.generate_monthly_breakdowns(
            "Test Goal", 
            "Test goal description", 
            2025
        )
        
        # Assertions
        self.assertEqual(len(breakdowns), 12)
        self.assertEqual(breakdowns[0]["month"], 1)
        self.assertEqual(breakdowns[0]["description"], "January milestone")
        
        # Check that OpenAI was called correctly
        mock_create.assert_called_once()
        # Verify model name was passed correctly
        args, kwargs = mock_create.call_args
        self.assertEqual(kwargs["model"], "o3-mini-2025-01-31")
        
        print("Monthly breakdowns generation test passed!")
    
    @patch('openai.chat.completions.create')
    def test_generate_goal_feedback(self, mock_create):
        """Test generating goal feedback with AI"""
        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {
            "feedback_text": "You're making excellent progress! Keep up the good work.",
            "feedback_type": "affirm"
        }
        '''
        mock_create.return_value = mock_response
        
        # Create test monthly breakdowns
        monthly_breakdowns = [
            {"month": 1, "description": "January milestone", "status": "ahead"},
            {"month": 2, "description": "February milestone", "status": "on_track"},
            {"month": 3, "description": "March milestone", "status": "behind"},
            {"month": 4, "description": "April milestone", "status": "not_started"}
        ]
        
        # Call the function
        feedback = self.ai_service.generate_goal_feedback(
            "Test Goal",
            "Test goal description",
            monthly_breakdowns,
            4  # Current month = April
        )
        
        # Assertions
        self.assertEqual(feedback["feedback_text"], "You're making excellent progress! Keep up the good work.")
        self.assertEqual(feedback["feedback_type"], "affirm")
        
        # Check that OpenAI was called correctly
        mock_create.assert_called_once()
        
        print("Goal feedback generation test passed!")

if __name__ == "__main__":
    unittest.main()
