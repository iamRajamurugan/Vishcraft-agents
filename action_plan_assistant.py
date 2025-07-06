


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
        # Enhanced prompt for more actionable and specific output
        prompt = (
            f"SYSTEM: You are a senior career planning expert. For the following user information, generate a highly actionable, detailed, and visually structured action plan and a precise list of skill gaps.\n"
            f"User's career paths: {career_paths}\nUser's current skills: {current_skills}\n"
            "The action plan must be tailored to the user's skills and the specified career paths. Include a timeline (Month 1, Month 2, etc.), milestones, and clear next steps. "
            "Use markdown formatting: bullet points, bold section headers, and tables if appropriate. "
            "Skill gaps must be a Python list of specific missing skills required for the career paths, based on the user's current skills. "
            "Return a Python dict with keys 'action_plan' (markdown str) and 'skill_gaps' (list of str). "
            "If information is missing, make reasonable assumptions and still provide a full, non-generic, and non-empty plan. Do not return placeholders or generic advice."
        )
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        text = response.text.strip()
        # DEBUG: Print the raw LLM output for troubleshooting
        print("\n[ActionPlanAssistant] Raw LLM output:\n", text)
        # Remove code block markers if present
        if text.startswith('```'):
            text = text.strip('`').split('\n', 1)[-1].strip()
        # Try to extract only the dict or variables from the LLM output
        import re
        result = None
        # 1. Try to extract a dict from anywhere in the output
        match = re.search(r"\{[\s\S]*?\}", text)
        if match:
            try:
                result = ast.literal_eval(match.group(0))
            except Exception:
                result = None
        # 2. If not found, try to extract action_plan and skill_gaps variables (robust fallback)
        if not result:
            # Try to extract everything between action_plan = and skill_gaps =
            action_plan = ""
            skill_gaps = []
            ap_start = text.find('action_plan =')
            sg_start = text.find('skill_gaps =')
            if ap_start != -1 and sg_start != -1:
                action_plan_raw = text[ap_start+len('action_plan ='):sg_start].strip()
                # Remove triple/single quotes if present
                action_plan_raw = re.sub(r'^[fr]?(["\"]).*?\1', '', action_plan_raw, flags=re.DOTALL)
                action_plan = action_plan_raw.strip('"\'\n ')
            elif ap_start != -1:
                # If skill_gaps not found, take everything after action_plan =
                action_plan = text[ap_start+len('action_plan ='):].strip('"\'\n ')
            # Try to extract skill_gaps as before
            skill_gaps_match = re.search(r"skill_gaps\s*=\s*(\[[^\]]*\])", text)
            if skill_gaps_match:
                try:
                    skill_gaps = ast.literal_eval(skill_gaps_match.group(1))
                except Exception:
                    skill_gaps = [skill_gaps_match.group(1)]
            result = {"action_plan": action_plan, "skill_gaps": skill_gaps}
        # 3. If still not found, fallback to the whole text
        if not result:
            result = {"action_plan": text, "skill_gaps": []}
        # Clean up action_plan: remove only the function definition line, not the body
        plan = result.get('action_plan', '')
        plan = re.sub(r'^def\s+\w+\(.*?\):\s*', '', plan, flags=re.MULTILINE)
        plan = re.split(r'Key Improvements|Explanations|```', plan, flags=re.IGNORECASE)[0].strip()
        # Ensure the plan is not empty or generic
        if not plan or plan.strip().lower() in ["no action plan generated.", "none", "undefined", "generic", "n/a"]:
            plan = "**No actionable plan could be generated. Please provide more specific skills and career paths.**"
        result['action_plan'] = plan
        # Clean up skill_gaps
        skill_gaps = result.get('skill_gaps', [])
        if isinstance(skill_gaps, str):
            try:
                skill_gaps = ast.literal_eval(skill_gaps)
            except Exception:
                skill_gaps = [skill_gaps]
        skill_gaps = [g for g in skill_gaps if g and str(g).lower() not in ["none", "undefined", "n/a"]]
        # If skill_gaps is empty, add a message for clarity
        if not skill_gaps:
            skill_gaps = ["No significant skill gaps identified based on your current skills and chosen career paths."]
        result['skill_gaps'] = skill_gaps
        return result

# Example usage:
# assistant = ActionPlanAssistant(api_key="YOUR_GEMINI_API_KEY")
# result = assistant.run({"career_paths": ["AI Researcher"], "current_skills": ["Python"]})
# print(result)
