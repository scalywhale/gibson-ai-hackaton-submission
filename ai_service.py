import openai
import json
from typing import List, Dict, Any

class AIService:
    def __init__(self, api_key):
        """Initialize the AI service with OpenAI API key"""
        openai.api_key = api_key
        # Use the specified model from requirements
        self.model = "o3-mini-2025-01-31"
    
    def generate_monthly_breakdowns(self, goal_title: str, goal_description: str, year: int) -> List[Dict[str, Any]]:
        """Generate monthly breakdowns for a yearly goal using OpenAI API"""
        prompt = f"""
        I'm planning to achieve the following goal in {year}:
        
        Goal: {goal_title}
        Description: {goal_description}
        
        Please create a monthly breakdown for this goal with specific milestones or actions for each month (January through December).
        Each month should have a clear, actionable description of what I should achieve.
        
        Format the response as JSON like this:
        {{
            "months": [
                {{"month": 1, "description": "January milestone"}},
                {{"month": 2, "description": "February milestone"}},
                ...and so on for all 12 months
            ]
        }}
        
        Only respond with the JSON object as specified above, no additional text.
        """
        
        try:
            # No temperature parameter as specified in requirements
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates monthly breakdowns for yearly goals."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            # Parse the content as JSON and extract the array
            result = json.loads(content)
            
            # Ensure we have a list
            if isinstance(result, dict) and "months" in result:
                return result["months"]
            elif isinstance(result, list):
                return result
            else:
                # Create a fallback list if format is unexpected
                return [{"month": i, "description": f"Month {i} milestone"} for i in range(1, 13)]
                
        except Exception as e:
            # Log error and return a default list
            print(f"Error generating monthly breakdowns: {str(e)}")
            return [{"month": i, "description": f"Month {i} milestone"} for i in range(1, 13)]
    
    def generate_goal_feedback(self, goal_title: str, goal_description: str, 
                              monthly_breakdowns: List[Dict], 
                              current_month: int) -> Dict[str, Any]:
        """Generate feedback on goal progress based on monthly statuses"""
        
        # Create a status summary to feed into the prompt
        status_summary = ""
        for breakdown in monthly_breakdowns:
            if breakdown["month"] <= current_month:
                status_summary += f"Month {breakdown['month']}: {breakdown['description']} - Status: {breakdown.get('status', 'unknown')}\n"
        
        prompt = f"""
        I'm tracking progress on this goal:
        
        Goal: {goal_title}
        Description: {goal_description}
        
        Here's my progress so far (we're currently in month {current_month}):
        
        {status_summary}
        
        Based on this progress, provide an analysis of my goal achievement and a recommendation.
        Choose exactly ONE of these recommendation types:
        1. "double_down" - if I need to focus more effort on this goal
        2. "reconsider" - if I should rethink my approach or adjust the goal
        3. "raise_the_bar" - if I'm doing so well I should set more ambitious targets
        4. "affirm" - if I'm on track and should continue as planned
        
        Format your response as a JSON object with these fields:
        - feedback_text: [your detailed analysis and advice]
        - feedback_type: [one of: "double_down", "reconsider", "raise_the_bar", "affirm"]
        
        Only respond with the JSON object, no additional text.
        """
        
        try:
            # No temperature parameter as specified in requirements
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a goal achievement analyst who provides constructive feedback."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
                
        except Exception as e:
            # Log error and return a default response
            print(f"Error generating goal feedback: {str(e)}")
            return {
                "feedback_text": "Unable to generate personalized feedback at this time.",
                "feedback_type": "affirm"
            }
