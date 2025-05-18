import streamlit as st
import datetime
import uuid
import json
from database import Database
from auth import Auth
from goals import GoalManager
from ai_service import AIService
import ui_components

# Load OpenAI API key
try:
    with open('openaikey.txt', 'r') as f:
        openai_api_key = f.read().strip()
except Exception as e:
    st.error(f"Failed to load OpenAI API key: {str(e)}")
    openai_api_key = ""

# Initialize components
auth = Auth()
goal_manager = GoalManager(openai_api_key)

# Set page config
st.set_page_config(
    page_title="Goal Tracker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
    
if 'user_uuid' not in st.session_state:
    st.session_state.user_uuid = None
    
if 'username' not in st.session_state:
    st.session_state.username = None
    
if 'goals' not in st.session_state:
    st.session_state.goals = []
    
if 'current_feedback' not in st.session_state:
    st.session_state.current_feedback = None
    
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = {}

# Auth callbacks
def login_callback(username, password):
    """Handle login form submission"""
    success, result = auth.login_user(username, password)
    if success:
        st.session_state.user_logged_in = True
        st.session_state.user_uuid = result
        st.session_state.username = username
        load_user_goals()
        st.success(f"Welcome back, {username}!")
        st.rerun()
    else:
        st.error(f"Login failed: {result}")

def signup_callback(username, password):
    """Handle signup form submission"""
    if len(username) < 3:
        st.error("Username must be at least 3 characters long")
        return
        
    if len(password) < 6:
        st.error("Password must be at least 6 characters long")
        return
        
    success, result = auth.register_user(username, password)
    if success:
        st.session_state.user_logged_in = True
        st.session_state.user_uuid = result
        st.session_state.username = username
        st.success(f"Welcome, {username}! Your account has been created.")
        st.rerun()
    else:
        st.error(f"Registration failed: {result}")

def logout():
    """Handle logout"""
    st.session_state.user_logged_in = False
    st.session_state.user_uuid = None
    st.session_state.username = None
    st.session_state.goals = []
    st.session_state.current_feedback = None
    st.rerun()

# Goal management callbacks
def load_user_goals():
    """Load goals for the current user"""
    if st.session_state.user_uuid:
        try:
            st.session_state.goals = goal_manager.get_user_goals(st.session_state.user_uuid)
            
            # Update debug info
            st.session_state.debug_info["goals_loaded"] = len(st.session_state.goals)
            st.session_state.debug_info["load_timestamp"] = datetime.datetime.now().isoformat()
        except Exception as e:
            st.error(f"Failed to load goals: {str(e)}")
            st.session_state.debug_info["load_error"] = str(e)

def create_goal_callback(title, description, year):
    """Handle goal creation"""
    try:
        with st.spinner("Creating goal and generating monthly breakdown with AI..."):
            goal_uuid = goal_manager.create_goal(
                st.session_state.user_uuid,
                title,
                description,
                year
            )
            
            # Update debug info
            st.session_state.debug_info["last_goal_created"] = {
                "uuid": goal_uuid,
                "title": title,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Reload goals
            load_user_goals()
            
            st.success("Goal created successfully with AI-generated monthly breakdown!")
    except Exception as e:
        st.error(f"Failed to create goal: {str(e)}")
        st.session_state.debug_info["create_goal_error"] = str(e)

def update_status_callback(breakdown_uuid, new_status):
    """Update the status of a monthly breakdown"""
    success = goal_manager.update_monthly_breakdown(breakdown_uuid, status=new_status)
    if success:
        # Reload goals to update the UI
        load_user_goals()
    else:
        st.error("Failed to update status")

def view_feedback_callback(goal_uuid):
    """Generate and display AI feedback for a goal"""
    with st.spinner("Analyzing goal progress and generating feedback..."):
        feedback = goal_manager.generate_feedback(goal_uuid)
        if feedback:
            st.session_state.current_feedback = feedback
            
            # Update debug info
            st.session_state.debug_info["last_feedback"] = {
                "goal_uuid": goal_uuid,
                "feedback_type": feedback.get("feedback_type", ""),
                "timestamp": datetime.datetime.now().isoformat()
            }
        else:
            st.error("Failed to generate feedback")

# Main application layout
def main():
    """Main application function"""
    ui_components.render_header()
    
    # Show logout button if logged in
    if st.session_state.user_logged_in:
        col1, col2 = st.columns([0.9, 0.1])
        with col2:
            st.button("Logout", on_click=logout)
        
        # Show goal creation if user has fewer than 2 goals
        if len(st.session_state.goals) < 2:
            ui_components.render_goal_creation_form(create_goal_callback)
            
        # Show goals timeline
        ui_components.render_year_timeline(
            st.session_state.goals,
            update_status_callback,
            view_feedback_callback
        )
        
        # Show feedback if available
        if st.session_state.current_feedback:
            ui_components.render_feedback(st.session_state.current_feedback)
            
        # Debug information (collapsed by default)
        ui_components.render_debug_info({
            "user_uuid": st.session_state.user_uuid,
            "username": st.session_state.username,
            "goal_count": len(st.session_state.goals),
            **st.session_state.debug_info
        })
    else:
        # Show login/signup forms
        ui_components.render_login_signup_forms(login_callback, signup_callback)

# Run the app
if __name__ == "__main__":
    main()
