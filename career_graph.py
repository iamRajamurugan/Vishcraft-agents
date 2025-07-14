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
        # Stage 1: Enhanced role fitting with personality inference
        role_result = role_fit.run(user_input)
       
        # Stage 2: Enhanced career path generation (vertical + lateral)
        path_input = {
            "recommended_roles": role_result["recommended_roles"],
            "personality_profile": role_result.get("personality_profile", {})
        }
        path_result = career_path.run(path_input)
      
        # Stage 3: Adaptive action plan generation
        action_input = {
            "career_paths": path_result["career_paths"],
            "current_skills": user_input.get("skills", []),
            "personality_profile": role_result.get("personality_profile", {})
        }
        action_result = action_plan.run(action_input)
    
        return {
            "role_fit": role_result,
            "career_path": path_result,
            "action_plan": action_result,
            "enhanced_features": {
                "personality_inference": True,
                "lateral_paths": True,
                "adaptive_planning": True,
                "monetization_ready": action_result.get("monetization_ready", False)
            }
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
