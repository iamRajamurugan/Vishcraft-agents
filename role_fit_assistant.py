


import google.generativeai as genai
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

    def run(self, input: Dict) -> Dict:
        skills = input.get('skills', [])
        interests = input.get('interests', [])
        experience = input.get('experience', 0)
        prompt = (
            f"Given the following skills: {skills}, interests: {interests}, and "
            f"years of experience: {experience}, suggest 3-5 suitable job roles. "
            "Return only a Python list of role names, no explanations, no extra text."
        )
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        # Clean up the LLM output to extract only the list
        text = response.text.strip()
        try:
            # Remove code block markers if present
            if text.startswith('```'):
                text = text.strip('`').split('\n', 1)[-1].strip()
            recommended_roles = ast.literal_eval(text)
            if not isinstance(recommended_roles, list):
                recommended_roles = [str(text)]
        except Exception:
            # Fallback: try to extract list from text
            import re
            matches = re.findall(r"\[(.*?)\]", text, re.DOTALL)
            if matches:
                try:
                    recommended_roles = ast.literal_eval(f"[{matches[0]}]")
                except Exception:
                    recommended_roles = [text]
            else:
                recommended_roles = [text]
        # Remove empty/undefined/duplicate entries
        recommended_roles = [r for r in recommended_roles if r and str(r).lower() != 'undefined']
        return {"recommended_roles": recommended_roles}

# Example usage:
# assistant = RoleFitAssistant(api_key="YOUR_GEMINI_API_KEY")
# result = assistant.run({"skills": ["Python", "Data Analysis"], "interests": ["AI"], "experience": 2})
# print(result)
