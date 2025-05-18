import streamlit as st
import datetime
from typing import Dict, List, Any, Callable

def render_header():
    """Render the app header"""
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.title("🎯 Goal Tracker")
        st.markdown("Set, track, and achieve your yearly goals with AI assistance")
    with col2:
        st.empty()  # Reserved for user profile info/logout

def render_login_signup_forms(login_callback: Callable, signup_callback: Callable):
    """Render login and signup forms"""
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if username and password:
                    login_callback(username, password)
                else:
                    st.error("Please fill in all fields")
                    
    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_button = st.form_submit_button("Sign Up")
            
            if submit_button:
                if new_username and new_password and confirm_password:
                    if new_password == confirm_password:
                        signup_callback(new_username, new_password)
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")

def render_goal_creation_form(create_goal_callback: Callable, year: int = None):
    """Render form for creating new goals"""
    if year is None:
        year = datetime.datetime.now().year
        
    st.subheader("Set Your Goals")
    st.markdown("Set up to two high-level goals for the year. Our AI will help break them down into monthly milestones.")
    
    with st.form("goal_form"):
        goal_title = st.text_input("Goal Title", placeholder="E.g., Learn a new programming language")
        goal_description = st.text_area("Goal Description", 
                                      placeholder="Add details about your goal, why it's important, and what success looks like")
        goal_year = st.selectbox("Year", 
                               options=[year-1, year, year+1], 
                               index=1)
        
        submit_button = st.form_submit_button("Create Goal & Generate Monthly Breakdown")
        
        if submit_button:
            if goal_title and goal_description:
                with st.spinner("Generating monthly breakdown with AI..."):
                    create_goal_callback(goal_title, goal_description, goal_year)
            else:
                st.error("Please provide both a title and description for your goal")

def render_year_timeline(goals_data: List[Dict[str, Any]], 
                        update_status_callback: Callable,
                        view_feedback_callback: Callable):
    """Render a visual timeline of the year with monthly goal tracking"""
    if not goals_data:
        st.info("No goals have been created yet. Create your first goal above.")
        return
        
    st.header("Year Timeline")
    
    # Month abbreviations
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    current_month = datetime.datetime.now().month
    
    # Create a goal section for each goal
    for goal in goals_data:
        st.subheader(f"Goal: {goal['title']}")
        
        # Show progress and status counts
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            progress = int(goal.get('progress_percent', 0))
            st.metric("Overall Progress", f"{progress}%")
        with col2:
            st.metric("Ahead", goal.get('ahead_count', 0), delta=None, delta_color="normal")
        with col3:
            st.metric("On Track", goal.get('on_track_count', 0), delta=None, delta_color="normal")
        with col4:
            st.metric("Behind", goal.get('behind_count', 0), delta=None, delta_color="off")
            
        # Create the month grid
        cols = st.columns(12)
        monthly_breakdowns = goal.get('monthly_breakdowns', [])
        
        # Dictionary to quickly access breakdowns by month
        breakdowns_by_month = {bd['month']: bd for bd in monthly_breakdowns}
        
        for i, month in enumerate(months):
            month_num = i + 1
            with cols[i]:
                # Highlight current month
                if month_num == current_month:
                    st.markdown(f"**{month}**")
                else:
                    st.markdown(month)
                
                # Show month's breakdown if it exists
                if month_num in breakdowns_by_month:
                    breakdown = breakdowns_by_month[month_num]
                    
                    # Color based on status
                    status = breakdown.get('status', 'not_started')
                    if status == 'ahead':
                        status_color = 'green'
                    elif status == 'on_track':
                        status_color = 'blue'
                    elif status == 'behind':
                        status_color = 'red'
                    else:
                        status_color = 'gray'
                    
                    # Show status selection for all months
                    new_status = st.selectbox(
                        f"Status", 
                        options=['not_started', 'ahead', 'on_track', 'behind'],
                        index=['not_started', 'ahead', 'on_track', 'behind'].index(status),
                        key=f"status_{goal['uuid']}_{month_num}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != status:
                        update_status_callback(breakdown['uuid'], new_status)
                    
                    # Format the milestone text with color
                    st.markdown(
                        f"<div style='background-color: {status_color}20; padding: 5px; "
                        f"border-left: 3px solid {status_color}; font-size: 0.8em; min-height: 80px;'>"
                        f"{breakdown['description']}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='background-color: #f0f0f0; padding: 5px; "
                        f"min-height: 80px; font-size: 0.8em;'>"
                        f"No milestone set"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
        # Button to generate feedback
        st.button("Get AI Feedback & Analysis", key=f"feedback_btn_{goal['uuid']}", 
                 on_click=lambda uuid=goal['uuid']: view_feedback_callback(uuid))
        st.divider()

def render_feedback(feedback_data: Dict[str, Any]):
    """Render AI feedback and analysis"""
    if not feedback_data:
        return
        
    st.header("Goal Analysis & Feedback")
    
    # Color coding for feedback types
    feedback_type = feedback_data.get('feedback_type', 'affirm')
    if feedback_type == 'double_down':
        icon = "🔥"
        color = "#FF9800"
        title = "Double Down"
    elif feedback_type == 'reconsider':
        icon = "🔄"
        color = "#F44336"
        title = "Reconsider Approach"
    elif feedback_type == 'raise_the_bar':
        icon = "⬆️"
        color = "#4CAF50"
        title = "Raise the Bar"
    else:  # affirm
        icon = "✅"
        color = "#2196F3"  
        title = "You're On Track"
    
    st.markdown(
        f"<div style='background-color: {color}20; padding: 15px; "
        f"border-left: 5px solid {color}; margin-bottom: 20px;'>"
        f"<h3 style='color: {color};'>{icon} {title}</h3>"
        f"<p>{feedback_data.get('feedback_text', '')}</p>"
        f"</div>",
        unsafe_allow_html=True
    )

def render_debug_info(debug_data: Dict[str, Any]):
    """Render debug information in a collapsible section"""
    with st.expander("Debug Information", expanded=False):
        st.json(debug_data)
