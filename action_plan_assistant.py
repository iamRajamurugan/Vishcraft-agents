import google.generativeai as genai
import re
from typing import List, Dict
import os
from dotenv import load_dotenv
import ast
import json
from datetime import datetime


class ActionPlanAssistant:
    def __init__(self, api_key: str = None, model: str = 'gemini-2.0-flash'):
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = model
        genai.configure(api_key=self.api_key)

    def _create_adaptive_plan(self, career_paths: List[str], current_skills: List[str], personality_profile: Dict) -> str:
        """Create an adaptive action plan that can be updated based on user progress"""
        prompt = (
            f"SYSTEM: You are a certified career mentor AI powered by a global L&D engine.\n\n"
            f"GOAL: Create a 12-month adaptive roadmap toward the chosen role track. This plan must:\n"
            f"- Be tailored to user goals\n"
            f"- Show realistic milestones\n"
            f"- Recommend courses and skill-building tasks\n"
            f"- Use a professional but motivational tone\n\n"
            f"INPUT:\n"
            f"Career_Paths: {career_paths}\n"
            f"Current_Skills: {current_skills}\n"
            f"Personality_Profile: {personality_profile}\n\n"
            f"OUTPUT: Return a markdown plan with:\n"
            f"1. Monthly Milestones (Month 1-12)\n"
            f"2. Skill Development Priorities\n"
            f"3. Progress Tracking Checkpoints\n"
            f"4. Course/Certification Recommendations\n"
            f"5. Networking Actions\n"
            f"6. Flexible alternatives for different scenarios\n\n"
            f"FORMAT: Use markdown with clear sections, timelines, and measurable goals. Make it actionable and trackable."
        )
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        
        return response.text.strip()

    def _identify_skill_gaps(self, career_paths: List[str], current_skills: List[str]) -> List[str]:
        """Identify specific skill gaps for the chosen career paths"""
        prompt = (
            f"SYSTEM: You are a precision skill auditor AI used in Fortune 500 hiring platforms.\n\n"
            f"GOAL: From the target path and user's current abilities, detect the most urgent skill gaps.\n\n"
            f"INPUT:\n"
            f"Career_Paths: {career_paths}\n"
            f"Current_Skills: {current_skills}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Identify the top 5-10 most critical skill gaps\n"
            f"- Focus on skills essential for success in these career paths\n"
            f"- Prioritize by impact and urgency\n\n"
            f"OUTPUT: Return a Python list of specific skill names that need to be addressed."
        )
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        
        try:
            text = response.text.strip()
            if text.startswith('```'):
                text = re.sub(r'```[a-zA-Z]*\n?', '', text).strip()
            
            skill_gaps = ast.literal_eval(text)
            if not isinstance(skill_gaps, list):
                skill_gaps = [text]
        except Exception:
            skill_gaps = ["Technical skills", "Leadership skills", "Industry knowledge"]
        
        return [gap for gap in skill_gaps if gap and str(gap).lower() not in ["none", "undefined", "n/a"]]

    def update_progress(self, input: Dict) -> Dict:
        """Update action plan based on user progress feedback"""
        completed_skills = input.get('completed_skills', [])
        current_plan = input.get('current_plan', '')
        career_paths = input.get('career_paths', [])
        remaining_skills = input.get('remaining_skills', [])
        
        prompt = (
            f"SYSTEM: You are an intelligent roadmap optimizer AI.\n\n"
            f"TASK: Given current plan and recent skill progress, adapt the plan in-place to reflect progress and refresh goals.\n\n"
            f"INPUT:\n"
            f"Completed_Skills: {completed_skills}\n"
            f"Remaining_Skills: {remaining_skills}\n"
            f"Career_Paths: {career_paths}\n"
            f"Current_Plan: {current_plan[:500]}...\n\n"
            f"OUTPUT: Return a Python dict with keys:\n"
            f"- 'updated_plan': markdown string with the revised plan\n"
            f"- 'new_recommendations': list of 3-5 new action items based on progress\n"
            f"- 'progress_percentage': numerical completion percentage\n"
            f"- 'motivation_message': personalized encouragement message\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Acknowledge completed skills\n"
            f"2. Adjust timeline for remaining goals\n"
            f"3. Add new recommendations based on progress\n"
            f"4. Provide motivation and next steps"
        )
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        
        try:
            text = response.text.strip()
            if text.startswith('```'):
                text = re.sub(r'```[a-zA-Z]*\n?', '', text).strip()
            
            update_result = ast.literal_eval(text)
            if not isinstance(update_result, dict):
                update_result = {
                    'updated_plan': text,
                    'new_recommendations': ['Continue with current plan'],
                    'progress_percentage': len(completed_skills) / max(len(completed_skills) + len(remaining_skills), 1) * 100
                }
        except Exception:
            update_result = {
                'updated_plan': f"Great progress on completing: {', '.join(completed_skills)}. Continue focusing on: {', '.join(remaining_skills[:3])}",
                'new_recommendations': ['Continue with current plan', 'Consider advanced courses'],
                'progress_percentage': len(completed_skills) / max(len(completed_skills) + len(remaining_skills), 1) * 100
            }
        
        return update_result

    def run(self, input: Dict) -> Dict:
        career_paths = input.get('career_paths', [])
        current_skills = input.get('current_skills', [])
        personality_profile = input.get('personality_profile', {})
        
        # Create adaptive action plan
        action_plan = self._create_adaptive_plan(career_paths, current_skills, personality_profile)
        
        # Identify skill gaps
        skill_gaps = self._identify_skill_gaps(career_paths, current_skills)
        
        # Create progress tracking structure
        progress_tracker = {
            "total_skills_needed": len(skill_gaps),
            "skills_completed": 0,
            "completion_percentage": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {
            "action_plan": action_plan,
            "skill_gaps": skill_gaps,
            "progress_tracker": progress_tracker,
            "plan_type": "adaptive",
            "monetization_ready": True,  # This output is ready for PDF/dashboard export
            "plan_summary": f"Generated adaptive plan with {len(skill_gaps)} skill gaps identified"
        }
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
        # Remove code block markers if present
        if text.startswith('```'):
            text = text.strip('`').split('\n', 1)[-1].strip()
        # Try to extract only the dict or variables from the LLM output
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
