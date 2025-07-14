


import google.generativeai as genai
import re
from typing import List, Dict
import os
from dotenv import load_dotenv
import ast


class RoleFitAssistant:
    def __init__(self, api_key: str = None, model: str = 'gemini-2.0-flash'):
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = model
        genai.configure(api_key=self.api_key)

    def _infer_personality_traits(self, skills: List[str], interests: List[str]) -> Dict:
        """Micro-agent for personality inference from skills and interests"""
        prompt = (
            f"SYSTEM: You are an advanced psychometric AI career analyst trained in behavioral modeling and occupational psychology.\n\n"
            f"TASK: Infer a detailed personality profile using the user's technical skills, soft skills, personal interests, and years of experience.\n\n"
            f"INPUT:\n"
            f"Skills: {skills}\n"
            f"Interests: {interests}\n\n"
            f"OUTPUT: Return a structured Python dict with these keys:\n"
            f"- personality_traits: array of 5 detailed traits\n"
            f"- dominant_behaviors: brief summary\n"
            f"- work_style: detailed work style preferences\n"
            f"- preferred_environment: startup/corporate/remote/etc\n\n"
            f"INSTRUCTIONS: Base personality on Big Five + Holland Code alignment. Be diagnostic and non-generic."
        )
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        
        try:
            # Clean and extract personality data
            text = response.text.strip()
            if text.startswith('```'):
                text = re.sub(r'```[a-zA-Z]*\n?', '', text).strip()
            
            personality_data = ast.literal_eval(text)
            if not isinstance(personality_data, dict):
                personality_data = {
                    'personality_traits': ['adaptable', 'analytical'],
                    'work_style': 'collaborative',
                    'preferred_environment': 'structured'
                }
        except Exception:
            personality_data = {
                'personality_traits': ['adaptable', 'analytical'],
                'work_style': 'collaborative', 
                'preferred_environment': 'structured'
            }
        
        return personality_data

    def run(self, input: Dict) -> Dict:
        skills = input.get('skills', [])
        interests = input.get('interests', [])
        experience = input.get('experience', 0)
        
        # Enhanced personality inference
        personality_data = self._infer_personality_traits(skills, interests)
        
        # Enhanced role matching with personality consideration
        prompt = (
            f"SYSTEM: You are a Senior AI Career Strategist embedded within a global talent analytics platform.\n\n"
            f"GOAL: Given a profile's technical + personality data, identify 5–7 job roles that align optimally with both aptitude and motivation.\n\n"
            f"INPUT:\n"
            f"Skills: {skills}\n"
            f"Interests: {interests}\n"
            f"Experience: {experience} years\n"
            f"Personality_Profile: {personality_data}\n\n"
            f"CONSTRAINTS:\n"
            f"- All roles must have 80%+ skill alignment\n"
            f"- Personality traits must align with role demands\n"
            f"- Work environment fit must be considered\n"
            f"- Avoid overly generic roles\n\n"
            f"OUTPUT: Return a Python list of specific job role titles. Each role must match both technical skills AND personality fit."
        )
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        
        try:
            text = response.text.strip()
            if text.startswith('```'):
                text = re.sub(r'```[a-zA-Z]*\n?', '', text).strip()
            
            recommended_roles = ast.literal_eval(text)
            if not isinstance(recommended_roles, list):
                recommended_roles = [str(response.text)]
        except Exception:
            recommended_roles = [str(response.text)]
        
        # Filter out any empty or undefined entries
        recommended_roles = [role for role in recommended_roles if role and str(role).lower() != 'undefined']
        
        return {
            "recommended_roles": recommended_roles,
            "personality_profile": personality_data,
            "profile_summary": f"Based on {len(skills)} skills and {len(interests)} interests with {experience} years of experience"
        }



# Within RoleFitAssistant:
# _infer_personality_traits - Micro-agent for personality inference
# Analyzes skills and interests to determine personality traits
# Infers work style preferences
# Identifies preferred work environment
# Within CareerPathAssistant:
# _generate_vertical_paths - Sub-agent for upward career progression
# _generate_lateral_paths - Sub-agent for sideways career transitions
# Within ActionPlanAssistant:
# _create_adaptive_plan - Enhanced planning engine
# update_progress - Progress tracking and plan adaptation system