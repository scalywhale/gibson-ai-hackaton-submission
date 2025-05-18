import os
import json
import uuid
import requests
from datetime import datetime
import re

class Database:
    def __init__(self):
        # Load Gibson AI project information
        try:
            with open('.gibsonai', 'r') as f:
                project_info = json.load(f)
                self.project_uuid = project_info.get('project_uuid')
                
            # Read API key from file specified in the instructions
            with open('openaikey.txt', 'r') as f:
                api_key_content = f.read().strip()
                
            # The API key from openaikey.txt is for OpenAI, not for Gibson
            # Get the Gibson API key from environment or project info
            gibson_api_key = os.environ.get('GIBSON_API_KEY', 
                                          "gAAAAABoKegtPFi_H_deoBWKdlhyzFvAZfOse38cQsVzNrFJJbAPpRyTzX82hcKJpcqn_OBF2PLANc6nf3cvuaONWsWjTTJVQTa-uDKDJTRLGwj1viSMs04=")
                
            self.api_key = gibson_api_key
            self.endpoint = "https://api.gibsonai.com/v1/-/query"
        except Exception as e:
            raise Exception(f"Failed to initialize database connection: {str(e)}")

    def escape_sql(self, value):
        """Escape string values for SQL queries to prevent SQL injection and syntax errors"""
        if value is None:
            return "NULL"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            # Replace single quotes with double single quotes (SQL standard for escaping)
            escaped = str(value).replace("'", "''")
            # Replace other potentially problematic characters
            escaped = re.sub(r'[\\\x00\n\r\x1a]', '', escaped)
            return f"'{escaped}'"
    
    def execute_query(self, query):
        """Execute a SQL query against the Gibson AI database"""
        headers = {"X-Gibson-API-Key": self.api_key}
        payload = {"query": query}
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Database query error: {str(e)}"
            if hasattr(e, 'response') and e.response:
                if e.response.text:
                    try:
                        error_details = e.response.json()
                        error_msg += f" - {error_details.get('detail', '')}"
                    except:
                        error_msg += f" - {e.response.text}"
            raise Exception(error_msg)

    # User operations
    def create_user(self, username, hashed_password):
        """Create a new user in the database"""
        user_uuid = str(uuid.uuid4())
        query = f"""
        INSERT INTO `user_profile` (`uuid`, `username`, `password`) 
        VALUES ({self.escape_sql(user_uuid)}, {self.escape_sql(username)}, {self.escape_sql(hashed_password)})
        """
        self.execute_query(query)
        return user_uuid

    def get_user_by_username(self, username):
        """Get user details by username"""
        query = f"""
        SELECT * FROM `user_profile` 
        WHERE `username` = {self.escape_sql(username)}
        """
        result = self.execute_query(query)
        if result and len(result) > 0:
            return result[0]
        return None

    def get_user_by_uuid(self, user_uuid):
        """Get user details by UUID"""
        query = f"""
        SELECT * FROM `user_profile` 
        WHERE `uuid` = {self.escape_sql(user_uuid)}
        """
        result = self.execute_query(query)
        if result and len(result) > 0:
            return result[0]
        return None

    # Goal operations
    def create_goal(self, user_uuid, title, description, year):
        """Create a new goal for the user"""
        goal_uuid = str(uuid.uuid4())
        
        # First get the user ID from UUID
        user = self.get_user_by_uuid(user_uuid)
        if not user:
            raise Exception("User not found")
            
        user_id = user['id']
        
        query = f"""
        INSERT INTO `goal` (`uuid`, `user_id`, `title`, `description`, `year`, `status`)
        VALUES ({self.escape_sql(goal_uuid)}, {user_id}, {self.escape_sql(title)}, {self.escape_sql(description)}, {year}, 'on_track')
        """
        self.execute_query(query)
        return goal_uuid

    def get_goals_by_user_uuid(self, user_uuid):
        """Get all goals for a specific user"""
        # First get the user ID from UUID
        user = self.get_user_by_uuid(user_uuid)
        if not user:
            raise Exception("User not found")
            
        user_id = user['id']
        
        query = f"""
        SELECT g.* FROM `goal` g
        WHERE g.`user_id` = {user_id}
        ORDER BY g.`year` DESC, g.`date_created` DESC
        """
        return self.execute_query(query)

    def get_goal_by_uuid(self, goal_uuid):
        """Get a goal by its UUID"""
        query = f"""
        SELECT * FROM `goal` 
        WHERE `uuid` = {self.escape_sql(goal_uuid)}
        """
        result = self.execute_query(query)
        if result and len(result) > 0:
            return result[0]
        return None

    def update_goal(self, goal_uuid, title=None, description=None, status=None):
        """Update a goal's details"""
        updates = []
        if title is not None:
            updates.append(f"`title` = {self.escape_sql(title)}")
        if description is not None:
            updates.append(f"`description` = {self.escape_sql(description)}")
        if status is not None:
            updates.append(f"`status` = {self.escape_sql(status)}")
            
        if not updates:
            return
            
        update_str = ", ".join(updates)
        query = f"""
        UPDATE `goal` 
        SET {update_str}
        WHERE `uuid` = {self.escape_sql(goal_uuid)}
        """
        self.execute_query(query)

    # Monthly Breakdown operations
    def create_monthly_breakdown(self, goal_uuid, month, description):
        """Create a monthly breakdown for a goal"""
        breakdown_uuid = str(uuid.uuid4())
        
        # First get the goal ID from UUID
        goal = self.get_goal_by_uuid(goal_uuid)
        if not goal:
            raise Exception("Goal not found")
            
        goal_id = goal['id']
        
        query = f"""
        INSERT INTO `goal_monthly_breakdown` 
        (`uuid`, `goal_id`, `month`, `description`, `status`)
        VALUES ({self.escape_sql(breakdown_uuid)}, {goal_id}, {month}, {self.escape_sql(description)}, 'not_started')
        """
        self.execute_query(query)
        return breakdown_uuid

    def get_monthly_breakdowns(self, goal_uuid):
        """Get all monthly breakdowns for a goal"""
        # First get the goal ID from UUID
        goal = self.get_goal_by_uuid(goal_uuid)
        if not goal:
            raise Exception("Goal not found")
            
        goal_id = goal['id']
        
        query = f"""
        SELECT * FROM `goal_monthly_breakdown` 
        WHERE `goal_id` = {goal_id}
        ORDER BY `month` ASC
        """
        return self.execute_query(query)

    def update_monthly_breakdown(self, breakdown_uuid, description=None, status=None):
        """Update a monthly breakdown"""
        updates = []
        if description is not None:
            updates.append(f"`description` = {self.escape_sql(description)}")
        if status is not None:
            updates.append(f"`status` = {self.escape_sql(status)}")
            
        if not updates:
            return
            
        update_str = ", ".join(updates)
        query = f"""
        UPDATE `goal_monthly_breakdown` 
        SET {update_str}
        WHERE `uuid` = {self.escape_sql(breakdown_uuid)}
        """
        self.execute_query(query)

    def get_monthly_breakdown_by_uuid(self, breakdown_uuid):
        """Get a monthly breakdown by its UUID"""
        query = f"""
        SELECT * FROM `goal_monthly_breakdown` 
        WHERE `uuid` = {self.escape_sql(breakdown_uuid)}
        """
        result = self.execute_query(query)
        if result and len(result) > 0:
            return result[0]
        return None

    # Feedback operations
    def create_feedback(self, goal_uuid, feedback_text, feedback_type):
        """Create feedback for a goal"""
        feedback_uuid = str(uuid.uuid4())
        
        # First get the goal ID from UUID
        goal = self.get_goal_by_uuid(goal_uuid)
        if not goal:
            raise Exception("Goal not found")
            
        goal_id = goal['id']
        
        query = f"""
        INSERT INTO `goal_feedback` 
        (`uuid`, `goal_id`, `feedback_text`, `feedback_type`)
        VALUES ({self.escape_sql(feedback_uuid)}, {goal_id}, {self.escape_sql(feedback_text)}, {self.escape_sql(feedback_type)})
        """
        self.execute_query(query)
        return feedback_uuid

    def get_feedback_for_goal(self, goal_uuid):
        """Get all feedback for a goal"""
        # First get the goal ID from UUID
        goal = self.get_goal_by_uuid(goal_uuid)
        if not goal:
            raise Exception("Goal not found")
            
        goal_id = goal['id']
        
        query = f"""
        SELECT * FROM `goal_feedback` 
        WHERE `goal_id` = {goal_id}
        ORDER BY `feedback_timestamp` DESC
        """
        return self.execute_query(query)
