# Career Guidance Tool with AI Agents

A multi-agent career guidance system built with Python and Google Gemini AI that provides personalized career recommendations, paths, and action plans.

## Overview

This system consists of three specialized AI agents working together in sequence:

1. **RoleFitAssistant**: Suggests suitable job roles based on your skills, interests, and experience.
2. **CareerPathAssistant**: Recommends career paths for each suggested role.
3. **ActionPlanAssistant**: Creates a personalized action plan and identifies skill gaps.

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## System Architecture

The system uses a simple Python orchestration pattern. Each agent is implemented as a separate Python class with a `run()` method. The agents are called in sequence, with each agent's output becoming input for the next.

- **Input**: User skills, interests, and experience level
- **Output**: Recommended roles, career paths, and an action plan with skill gaps

## Files

- `role_fit_assistant.py`: Determines suitable job roles
- `career_path_assistant.py`: Suggests career paths for each role
- `action_plan_assistant.py`: Creates a personalized action plan
- `career_graph.py`: Orchestrates the agents in sequence
- `app.py`: Streamlit web interface
- `.env`: Environment variables for API keys
- `requirements.txt`: Required Python packages

## License

MIT
