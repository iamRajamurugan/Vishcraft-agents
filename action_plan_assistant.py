


import google.generativeai as genai
from typing import List, Dict
import os
from dotenv import load_dotenv
import ast


class ActionPlanAssistant:
    def __init__(self, api_key: str = None, model: str = 'gemini-2.0-flash'):
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = model
        genai.configure(api_key=self.api_key)

    def run(self, input: Dict) -> Dict:
        career_paths = input.get('career_paths', [])
        current_skills = input.get('current_skills', [])
        prompt = (
            f"SYSTEM: You are a career planning expert. You must ALWAYS generate a creative, professional, and visually structured action plan to pursue the given career paths, even if the user's skills or interests are generic, incomplete, or missing. "
            f"User's career paths: {career_paths}\nUser's current skills: {current_skills}\n"
            "The plan should include a timeline (e.g., Month 1, Month 2, etc.), milestones, and clear next steps. "
            "Format the action plan as markdown with bullet points, bold section headers, and a table if appropriate. "
            "Also, list any skill gaps as a Python list (no explanations, just the list). "
            "Return a Python dict with keys 'action_plan' (markdown str) and 'skill_gaps' (list of str). "
            "If information is missing, make reasonable assumptions and still provide a full plan. Never return an empty or generic response."
        )
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove code block markers if present
        if text.startswith('```'):
            text = text.strip('`').split('\n', 1)[-1].strip()
        # Try to extract only the dict
        try:
            result = ast.literal_eval(text)
            if not isinstance(result, dict):
                result = {"action_plan": str(text), "skill_gaps": []}
        except Exception:
            import re
            # Try to extract dict from text
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    result = ast.literal_eval(match.group(0))
                except Exception:
                    result = {"action_plan": text, "skill_gaps": []}
            else:
                result = {"action_plan": text, "skill_gaps": []}
        # Clean up action_plan: remove any unwanted sections
        plan = result.get('action_plan', '')
        # Remove function definitions if present
        import re
        plan = re.sub(r'def\s+\w+\(.*?\):.*', '', plan, flags=re.DOTALL)
        # Remove any trailing explanations or code blocks
        plan = re.split(r'Key Improvements|Explanations|```', plan, flags=re.IGNORECASE)[0].strip()
        result['action_plan'] = plan
        # Clean up skill_gaps
        skill_gaps = result.get('skill_gaps', [])
        if isinstance(skill_gaps, str):
            # Try to parse as list
            try:
                skill_gaps = ast.literal_eval(skill_gaps)
            except Exception:
                skill_gaps = [skill_gaps]
        skill_gaps = [g for g in skill_gaps if g and str(g).lower() != 'undefined']
        result['skill_gaps'] = skill_gaps
        return result

# Example usage:
# assistant = ActionPlanAssistant(api_key="YOUR_GEMINI_API_KEY")
# result = assistant.run({"career_paths": ["AI Researcher"], "current_skills": ["Python"]})
# print(result)
