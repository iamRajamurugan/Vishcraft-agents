# LLM Prompt Templates for HR Enhancement

This document contains all the prompt templates used in the Vishcraft Career Guidance Multi-Agent System. These prompts are extracted directly from the codebase for HR review and enhancement.

## 1. RoleFitAssistant Prompts

### 1.1 Personality Inference Micro-Agent
**Location:** `role_fit_assistant.py` - `_infer_personality_traits()` method

**Current Prompt:**
```python
prompt = (
    f"Based on these skills: {skills} and interests: {interests}, "
    "infer 3-5 key personality traits that would influence career fit. "
    "Return as a Python dict with keys: 'personality_traits', 'work_style', 'preferred_environment'. "
    "Example: {'personality_traits': ['analytical', 'creative'], 'work_style': 'collaborative', 'preferred_environment': 'fast-paced'}"
)
```

**Variables:**
- `skills`: List of user skills
- `interests`: List of user interests

**Output Format:** Python dictionary
**Purpose:** Analyze skills/interests to infer personality traits for better role matching

---

### 1.2 Enhanced Role Matching
**Location:** `role_fit_assistant.py` - `run()` method

**Current Prompt:**
```python
prompt = (
    f"You are a senior career counselor. Based on the following profile:\n"
    f"Skills: {skills}\n"
    f"Interests: {interests}\n"
    f"Experience: {experience} years\n"
    f"Personality traits: {personality_data['personality_traits']}\n"
    f"Work style: {personality_data['work_style']}\n"
    f"Preferred environment: {personality_data['preferred_environment']}\n\n"
    "Suggest 5-7 highly suitable job roles that align with both technical skills AND personality fit. "
    "Consider roles that match the person's natural work style and environmental preferences. "
    "Return only a Python list of role names, no explanations."
)
```

**Variables:**
- `skills`: List of user skills
- `interests`: List of user interests  
- `experience`: Years of experience (integer)
- `personality_data`: Dictionary with personality traits, work style, preferred environment

**Output Format:** Python list of role names
**Purpose:** Match users to roles based on skills AND personality fit

---

## 2. CareerPathAssistant Prompts

### 2.1 Vertical Career Paths
**Location:** `career_path_assistant.py` - `_generate_vertical_paths()` method

**Current Prompt:**
```python
prompt = (
    f"For these roles: {roles}, create 2-3 vertical career progression paths for each role. "
    "Show clear advancement from entry-level to senior-level positions. "
    "Format: 'Role → Senior Role → Executive Role'. "
    "Return as a Python list of progression strings."
)
```

**Variables:**
- `roles`: List of recommended roles from RoleFitAssistant

**Output Format:** Python list of progression strings
**Purpose:** Generate upward career advancement paths

---

### 2.2 Lateral Career Paths
**Location:** `career_path_assistant.py` - `_generate_lateral_paths()` method

**Current Prompt:**
```python
prompt = (
    f"For these roles: {roles}, create 2-3 lateral career transition paths for each role. "
    "Show how someone can move sideways to related fields or industries. "
    "Focus on transferable skills and adjacent opportunities. "
    "Format: 'Current Role → Related Role → Alternative Role'. "
    "Return as a Python list of transition strings."
)
```

**Variables:**
- `roles`: List of recommended roles from RoleFitAssistant

**Output Format:** Python list of transition strings
**Purpose:** Generate sideways career transition opportunities

---

## 3. ActionPlanAssistant Prompts

### 3.1 Adaptive Action Plan Creation
**Location:** `action_plan_assistant.py` - `_create_adaptive_plan()` method

**Current Prompt:**
```python
prompt = (
    f"SYSTEM: You are a senior career planning expert. Create a comprehensive, adaptive action plan.\n"
    f"Career paths: {career_paths}\n"
    f"Current skills: {current_skills}\n"
    f"Personality profile: {personality_profile}\n\n"
    "Create a detailed action plan with the following structure:\n"
    "1. Monthly milestones (Month 1-12)\n"
    "2. Skill development priorities\n"
    "3. Progress tracking checkpoints\n"
    "4. Flexible alternatives for different scenarios\n\n"
    "Format as markdown with clear sections, timelines, and measurable goals. "
    "Include specific courses, certifications, projects, and networking strategies. "
    "Make it actionable and trackable."
)
```

**Variables:**
- `career_paths`: List of career paths from CareerPathAssistant
- `current_skills`: List of user's current skills
- `personality_profile`: Dictionary with personality data

**Output Format:** Markdown formatted action plan
**Purpose:** Create comprehensive, adaptive career action plans

---

### 3.2 Skill Gap Identification
**Location:** `action_plan_assistant.py` - `_identify_skill_gaps()` method

**Current Prompt:**
```python
prompt = (
    f"Given these career paths: {career_paths} and current skills: {current_skills}, "
    "identify the top 5-10 most critical skill gaps that need to be addressed. "
    "Focus on skills that are essential for success in these career paths. "
    "Return as a Python list of specific skill names."
)
```

**Variables:**
- `career_paths`: List of career paths
- `current_skills`: List of user's current skills

**Output Format:** Python list of skill names
**Purpose:** Identify critical missing skills for career advancement

---

### 3.3 Progress Update and Plan Adaptation
**Location:** `action_plan_assistant.py` - `update_progress()` method

**Current Prompt:**
```python
prompt = (
    f"SYSTEM: Update the existing action plan based on user progress.\n"
    f"Completed skills: {completed_skills}\n"
    f"Remaining skills: {remaining_skills}\n"
    f"Career paths: {career_paths}\n"
    f"Current plan: {current_plan[:500]}...\n\n"
    "Create an updated action plan that:\n"
    "1. Acknowledges completed skills\n"
    "2. Adjusts timeline for remaining goals\n"
    "3. Adds new recommendations based on progress\n"
    "4. Provides motivation and next steps\n\n"
    "Return as a Python dict with keys: 'updated_plan' (markdown string), 'new_recommendations' (list), 'progress_percentage' (number)."
)
```

**Variables:**
- `completed_skills`: List of skills user has completed
- `remaining_skills`: List of skills still to complete
- `career_paths`: List of career paths
- `current_plan`: Current action plan (truncated to 500 chars)

**Output Format:** Python dictionary with updated plan data
**Purpose:** Adapt action plans based on user progress

---

### 3.4 Legacy Enhanced Action Plan (Alternative Implementation)
**Location:** `action_plan_assistant.py` - `run()` method (legacy version)

**Current Prompt:**
```python
prompt = (
    f"SYSTEM: You are a senior career planning expert. For the following user information, generate a highly actionable, detailed, and visually structured action plan and a precise list of skill gaps.\n"
    f"User's career paths: {career_paths}\nUser's current skills: {current_skills}\n"
    "The action plan must be tailored to the user's skills and the specified career paths. Include a timeline (Month 1, Month 2, etc.), milestones, and clear next steps. "
    "Use markdown formatting: bullet points, bold section headers, and tables if appropriate. "
    "Skill gaps must be a Python list of specific missing skills required for the career paths, based on the user's current skills. "
    "Return a Python dict with keys 'action_plan' (markdown str) and 'skill_gaps' (list of str). "
    "If information is missing, make reasonable assumptions and still provide a full, non-generic, and non-empty plan. Do not return placeholders or generic advice."
)
```

**Variables:**
- `career_paths`: List of career paths
- `current_skills`: List of user's current skills

**Output Format:** Python dictionary with action_plan and skill_gaps
**Purpose:** Generate comprehensive action plans with skill gap analysis

---

## HR Enhancement Guidelines

### 1. Prompt Quality Considerations
- **Clarity**: Ensure prompts are specific and unambiguous
- **Context**: Provide sufficient context for the LLM to generate quality responses
- **Output Format**: Clearly specify expected output format (Python dict, list, markdown, etc.)
- **Error Handling**: Consider edge cases and provide fallback instructions

### 2. Variables to Validate
- All prompts use f-string formatting with dynamic variables
- Ensure variables are properly validated before prompt injection
- Consider sanitization for user-provided data

### 3. Consistency Opportunities
- Standardize prompt structure across all agents
- Use consistent terminology and language style
- Align output formats where possible

### 4. Enhancement Areas
- **Personality Analysis**: Could be expanded with more psychological frameworks
- **Career Path Diversity**: Consider adding industry-specific paths
- **Action Plan Granularity**: Could include more specific timelines and metrics
- **Progress Tracking**: Could add more sophisticated progress indicators

### 5. Professional Language
- All prompts should maintain professional, HR-appropriate language
- Consider cultural sensitivity and inclusivity
- Ensure compliance with HR policies and guidelines

---

## Technical Notes

### Model Configuration
- All agents use `gemini-2.0-flash` model by default
- API key managed through environment variables
- Error handling includes fallback responses for each prompt

### Output Parsing
- Most prompts expect structured output (Python dict/list)
- Code includes robust parsing with fallbacks
- AST literal evaluation used for safe parsing

### Integration Points
- Prompts are designed to work together in a pipeline
- Output from one agent feeds into the next
- Personality data flows through the entire system

---

*This document represents the current state of all LLM prompts in the Vishcraft Career Guidance System as of the latest update. For any modifications, please ensure consistency across the entire prompt ecosystem.*
