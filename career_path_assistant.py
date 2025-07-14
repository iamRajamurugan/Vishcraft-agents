
import google.generativeai as genai
import re
from typing import List, Dict
import os
from dotenv import load_dotenv
import ast


class CareerPathAssistant:
    def __init__(self, api_key: str = None, model: str = 'gemini-2.0-flash'):
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = model
        genai.configure(api_key=self.api_key)

    def _generate_vertical_paths(self, roles: List[str]) -> List[str]:
        """Generate vertical (upward) career progression paths"""
        prompt = (
            f"SYSTEM: You are a career trajectory architect specializing in vertical growth maps across industries.\n\n"
            f"GOAL: Generate structured career ladders for each given role.\n\n"
            f"INPUT:\n"
            f"Roles: {roles}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Show a minimum of 3 stages: Entry → Mid → Advanced\n"
            f"- For each role, create 2-3 clear advancement paths\n"
            f"- Format as 'Role → Senior Role → Executive Role'\n\n"
            f"OUTPUT: Return a Python list of progression strings. Each string should represent a complete career path."
        )
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        
        try:
            text = response.text.strip()
            if text.startswith('```'):
                text = re.sub(r'```[a-zA-Z]*\n?', '', text).strip()
            
            vertical_paths = ast.literal_eval(text)
            if not isinstance(vertical_paths, list):
                vertical_paths = [str(response.text)]
        except Exception:
            vertical_paths = [f"Junior {role} → Senior {role} → Lead {role}" for role in roles[:3]]
        
        return vertical_paths

    def _generate_lateral_paths(self, roles: List[str]) -> List[str]:
        """Generate lateral (sideways) career transition paths"""
        prompt = (
            f"SYSTEM: You are an occupational pathways engineer trained in cognitive skill portability.\n\n"
            f"GOAL: For each suggested role, identify realistic adjacent roles the user could move to using transferable skills.\n\n"
            f"INPUT:\n"
            f"Roles: {roles}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Include at least 2 lateral options per role\n"
            f"- Focus on roles that leverage similar skill sets but in different contexts\n"
            f"- Format as 'Current Role → Related Role → Alternative Role'\n\n"
            f"OUTPUT: Return a Python list of transition strings. Each string should represent a complete lateral path."
        )
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        
        try:
            text = response.text.strip()
            if text.startswith('```'):
                text = re.sub(r'```[a-zA-Z]*\n?', '', text).strip()
            
            lateral_paths = ast.literal_eval(text)
            if not isinstance(lateral_paths, list):
                lateral_paths = [str(response.text)]
        except Exception:
            lateral_paths = [f"{role} → Product Manager → Consultant" for role in roles[:3]]
        
        return lateral_paths

    def run(self, input: Dict) -> Dict:
        roles = input.get('recommended_roles', [])
        personality_profile = input.get('personality_profile', {})
        
        # Generate both vertical and lateral paths
        vertical_paths = self._generate_vertical_paths(roles)
        lateral_paths = self._generate_lateral_paths(roles)
        
        # Combine and clean paths
        all_paths = vertical_paths + lateral_paths
        career_paths = [path for path in all_paths if path and str(path).lower() != 'undefined']
        
        return {
            "career_paths": career_paths,
            "vertical_paths": vertical_paths,
            "lateral_paths": lateral_paths,
            "path_summary": f"Generated {len(vertical_paths)} vertical and {len(lateral_paths)} lateral career paths"
        }

# Example usage:
# assistant = CareerPathAssistant(api_key="YOUR_GEMINI_API_KEY")
# result = assistant.run({"recommended_roles": ["Data Scientist"]})
# print(result)
