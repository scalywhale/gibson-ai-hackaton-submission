# Goal Tracker App

A productivity application that helps professionals set and track their yearly goals using AI-powered suggestions and analysis.

## Features

- **User Authentication**: Simple signup with username and password
- **Goal Setting**: Set two high-level yearly goals
- **AI Suggestions**: Receive AI-powered monthly breakdowns for each goal
- **Timeline View**: Visualize goals on a yearly timeline with monthly progress
- **Status Tracking**: Set monthly check-in status (ahead/behind) with color coding
- **Performance Analysis**: Get AI-generated feedback on goal progress
- **Responsive Design**: Clean, minimal UI that adapts to different screen sizes

## Technology Stack

- **Frontend**: Streamlit for a sleek and minimal UI
- **Backend**: Gibson AI for database management
- **AI Integration**: OpenAI API (o3-mini-2025-01-31 model)
- **Database**: MySQL (hosted via Gibson AI)

## Project Structure

```
/Goal_Tracker_App
├── .gibsonai           # Gibson AI project configuration
├── app.py              # Main Streamlit application
├── database.py         # Database operations and connections
├── auth.py             # Authentication functionality
├── goals.py            # Goal management functionality
├── ai_service.py       # OpenAI integration for suggestions and analysis
├── ui_components.py    # Reusable UI components
├── tests/              # Test files for database and functionality
└── requirements.txt    # Project dependencies
```

## Database Schema

- **user_profile**: User account information with secure password storage
- **goal**: High-level goals linked to users
- **goal_monthly_breakdown**: Monthly milestones for each goal
- **goal_feedback**: AI-generated analysis and recommendations

## Current Status

- Initial setup complete
- Database schema designed and deployed
- Gibson AI integration completed
- User authentication implemented
- Goal setting and tracking functionality implemented
- AI suggestion system implemented
- Timeline view implemented

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `streamlit run app.py`
3. Access the app at http://localhost:8501
