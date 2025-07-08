from typing import Dict
import os
from dotenv import load_dotenv

from role_fit_assistant import RoleFitAssistant
from career_path_assistant import CareerPathAssistant
from action_plan_assistant import ActionPlanAssistant

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')

# Instantiate agents
role_fit = RoleFitAssistant(api_key=GEMINI_API_KEY)
career_path = CareerPathAssistant(api_key=GEMINI_API_KEY)
action_plan = ActionPlanAssistant(api_key=GEMINI_API_KEY)


def build_career_graph():
    def run(user_input):
        
        role_result = role_fit.run(user_input)
       
        path_result = career_path.run(role_result)
      
        action_input = {
            "career_paths": path_result["career_paths"],
            "current_skills": user_input.get("skills", [])
        }
        action_result = action_plan.run(action_input)
    
        return {
            "role_fit": role_result,
            "career_path": path_result,
            "action_plan": action_result
        }
    return type("CareerGraph", (), {"run": staticmethod(run)})

if __name__ == "__main__":
    sample_input = {
        "skills": ["Python", "Machine Learning", "Data Visualization"],
        "interests": ["AI", "Healthcare"],
        "experience": 3
    }
    graph = build_career_graph()

    results = graph.run(sample_input)
    print("\nFinal Results:")
    print(results)
