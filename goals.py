import datetime
from typing import List, Dict, Any
from database import Database
from ai_service import AIService

class GoalManager:
    def __init__(self, openai_api_key):
        self.db = Database()
        self.ai_service = AIService(openai_api_key)
        
    def create_goal(self, user_uuid: str, title: str, description: str, year: int) -> str:
        """Create a new goal and generate monthly breakdowns using AI"""
        # Create the goal in the database
        goal_uuid = self.db.create_goal(user_uuid, title, description, year)
        
        # Generate monthly breakdowns using AI
        monthly_breakdowns = self.ai_service.generate_monthly_breakdowns(title, description, year)
        
        # Save each monthly breakdown
        for breakdown in monthly_breakdowns:
            month = breakdown.get('month', 0)
            description = breakdown.get('description', '')
            
            if 1 <= month <= 12 and description:
                self.db.create_monthly_breakdown(goal_uuid, month, description)
        
        return goal_uuid
    
    def get_user_goals(self, user_uuid: str) -> List[Dict[str, Any]]:
        """Get all goals for a user with their monthly breakdowns"""
        goals = self.db.get_goals_by_user_uuid(user_uuid)
        
        # Enhance each goal with its monthly breakdowns
        enhanced_goals = []
        for goal in goals:
            goal_data = dict(goal)
            goal_data['monthly_breakdowns'] = self.db.get_monthly_breakdowns(goal['uuid'])
            goal_data['feedback'] = self.db.get_feedback_for_goal(goal['uuid'])
            enhanced_goals.append(goal_data)
            
        return enhanced_goals
    
    def update_goal(self, goal_uuid: str, title: str = None, description: str = None, status: str = None) -> bool:
        """Update a goal's details"""
        try:
            self.db.update_goal(goal_uuid, title, description, status)
            return True
        except Exception as e:
            print(f"Error updating goal: {str(e)}")
            return False
    
    def update_monthly_breakdown(self, breakdown_uuid: str, description: str = None, status: str = None) -> bool:
        """Update a monthly breakdown"""
        try:
            self.db.update_monthly_breakdown(breakdown_uuid, description, status)
            return True
        except Exception as e:
            print(f"Error updating monthly breakdown: {str(e)}")
            return False
    
    def generate_feedback(self, goal_uuid: str) -> Dict[str, Any]:
        """Generate AI feedback for a goal based on its current progress"""
        # Get the goal details
        goal = self.db.get_goal_by_uuid(goal_uuid)
        if not goal:
            return None
        
        # Get the monthly breakdowns
        monthly_breakdowns = self.db.get_monthly_breakdowns(goal_uuid)
        
        # Get current month
        current_month = datetime.datetime.now().month
        
        # Generate AI feedback
        feedback = self.ai_service.generate_goal_feedback(
            goal['title'],
            goal['description'],
            monthly_breakdowns,
            current_month
        )
        
        # Save the feedback to the database
        if feedback:
            self.db.create_feedback(
                goal_uuid,
                feedback['feedback_text'],
                feedback['feedback_type']
            )
        
        return feedback
            
    def get_goal_status_summary(self, goal_uuid: str) -> Dict[str, Any]:
        """Get a summary of the goal status including progress percentage"""
        # Get the goal
        goal = self.db.get_goal_by_uuid(goal_uuid)
        if not goal:
            return None
            
        # Get monthly breakdowns
        breakdowns = self.db.get_monthly_breakdowns(goal_uuid)
        
        # Current month as of now
        current_month = datetime.datetime.now().month
        
        # Count statuses
        total_months = min(current_month, len(breakdowns))
        if total_months == 0:
            return {
                'goal': goal,
                'progress_percent': 0,
                'ahead_count': 0,
                'on_track_count': 0,
                'behind_count': 0
            }
            
        ahead_count = sum(1 for b in breakdowns if b.get('status') == 'ahead' and b.get('month') <= current_month)
        on_track_count = sum(1 for b in breakdowns if b.get('status') == 'on_track' and b.get('month') <= current_month)
        behind_count = sum(1 for b in breakdowns if b.get('status') == 'behind' and b.get('month') <= current_month)
        
        # Calculate progress as weighted average
        # Ahead months count as 110%, on track as 100%, behind as 70%
        weighted_progress = (ahead_count * 1.1 + on_track_count * 1.0 + behind_count * 0.7) / total_months
        progress_percent = min(100, int(weighted_progress * 100))
        
        return {
            'goal': goal,
            'progress_percent': progress_percent,
            'ahead_count': ahead_count,
            'on_track_count': on_track_count,
            'behind_count': behind_count
        }
