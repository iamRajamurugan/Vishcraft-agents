
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

    def run(self, input: Dict) -> Dict:
        roles = input.get('recommended_roles', [])
        prompt = (
            f"Given the following recommended roles: {roles}, suggest 2-3 potential career paths for each role. "
            "Return only a Python list of career path names (flattened), no explanations, no extra text."
        )
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        text = response.text.strip()
        try:
            if text.startswith('```'):
                text = text.strip('`').split('\n', 1)[-1].strip()
            career_paths = ast.literal_eval(text)
            if not isinstance(career_paths, list):
                career_paths = [str(text)]
        except Exception:
            matches = re.findall(r"\[(.*?)\]", text, re.DOTALL)
            if matches:
                try:
                    career_paths = ast.literal_eval(f"[{matches[0]}]")
                except Exception:
                    career_paths = [text]
            else:
                career_paths = [text]
        career_paths = [p for p in career_paths if p and str(p).lower() != 'undefined']
        return {"career_paths": career_paths}

# Example usage:
# assistant = CareerPathAssistant(api_key="YOUR_GEMINI_API_KEY")
# result = assistant.run({"recommended_roles": ["Data Scientist"]})
# print(result)
