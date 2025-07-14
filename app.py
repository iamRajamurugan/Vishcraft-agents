import streamlit as st
from career_graph import build_career_graph
import json
import time
from datetime import datetime
import os
from export_utils import export_results_as_json, format_results_as_markdown

# Page configuration
st.set_page_config(
    page_title="VishCraft Career Guidance",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        # Fallback CSS if file doesn't exist
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: 700;
                color: #1E88E5;
                text-align: center;
                margin-bottom: 1rem;
            }
            .sub-header {
                font-size: 1.2rem;
                font-weight: 400;
                color: #424242;
                text-align: center;
                margin-bottom: 2rem;
            }
            .card {
                padding: 1.5rem;
                border-radius: 0.5rem;
                background-color: #f8f9fa;
                border-left: 4px solid #1E88E5;
                margin-bottom: 1rem;
            }
            .success-card {
                padding: 1.5rem;
                border-radius: 0.5rem;
                background-color: #f1f8e9;
                border-left: 4px solid #43a047;
                margin-bottom: 1rem;
            }
            .warning-card {
                padding: 1.5rem;
                border-radius: 0.5rem;
                background-color: #fff8e1;
                border-left: 4px solid #ffa000;
                margin-bottom: 1rem;
            }
            .section-title {
                font-size: 1.3rem;
                font-weight: 600;
                color: #1E88E5;
                margin-top: 1rem;
                margin-bottom: 0.8rem;
            }
            .list-item {
                padding: 0.5rem;
                border-radius: 0.3rem;
                background-color: #f5f5f5;
                margin-bottom: 0.5rem;
            }
            .stButton button {
                background-color: #1E88E5;
                color: white;
                font-weight: 500;
                padding: 0.5rem 1rem;
                border-radius: 0.3rem;
                width: 100%;
            }
        </style>
        """, unsafe_allow_html=True)

# Apply custom CSS
local_css("assets/style.css")

# Check API key configuration
def check_api_key():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
        st.error("🔑 **API Key Not Configured!**")
        st.markdown("""
        **To use this application, you need a valid Gemini API key:**
        1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Sign in with your Google account
        3. Create a new API key
        4. Copy the API key
        5. Edit the `.env` file in your project folder
        6. Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key
        7. Save the file and refresh this page
        """)
        st.stop()

check_api_key()

# Sidebar
with st.sidebar:
    try:
        st.image("assets/brain_icon.png", width=80)
    except:
        st.image("https://img.icons8.com/fluency/96/000000/brain.png", width=80)
    st.markdown("<div class='success-card'>VishCraft AI Career Guidance</div>", unsafe_allow_html=True)
    st.markdown("### How It Works")
    st.markdown("""
    1. **RoleFitAssistant** 👔 \n   Analyzes your skills and interests to suggest suitable roles
    
    2. **CareerPathAssistant** 🛣️ \n   Maps potential career paths for each role
    
    3. **ActionPlanAssistant** 📝 \n   Creates a personalized plan and identifies skill gaps
    """)
    
    st.markdown("---")
    st.markdown("### Tips for Best Results")
    st.markdown("""
    - Be specific with your skills
    - Include both technical and soft skills
    - Add varied interests to explore more options
    """)
    
    # History feature in sidebar
    st.markdown("---")
    st.markdown("### 📋 Previous Searches")
    
    # Load history from session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # Display history
    if not st.session_state.history:
        st.info("Your search history will appear here")
    else:
        for idx, item in enumerate(st.session_state.history):
            if st.button(f"Load: {', '.join(item['skills'][:2])}... ({len(item['roles'])} roles)", key=f"hist_{idx}"):
                st.session_state.load_item = item
                st.rerun()

# Main content
st.markdown("<h1 class='main-header'>VishCraft AI Career Guidance</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Discover your ideal career path with AI-powered guidance</p>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["🔍 Career Finder", "📊 Results", "📈 Progress Tracker"])

with tab1:
    st.markdown("### 🎯 Tell us about yourself")
    st.markdown("Enter your skills, interests, and experience to get personalized career recommendations")
    st.markdown("---")
    
    with st.form("career_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        # Pre-fill form if loading from history
        if 'load_item' in st.session_state:
            default_skills = ", ".join(st.session_state.load_item['skills'])
            default_interests = ", ".join(st.session_state.load_item['interests'])
            default_exp = st.session_state.load_item['experience']
            # Clear load_item after using it
            del st.session_state.load_item
        else:
            default_skills = ""
            default_interests = ""
            default_exp = 1
        
        with col1:
            skills = st.text_area(
                "Skills 💻",
                value=default_skills,
                placeholder="e.g. Python, Data Analysis, Communication, Leadership",
                help="Include both technical and soft skills for better recommendations"
            )
            
        with col2:
            interests = st.text_area(
                "Interests 🌟", 
                value=default_interests,
                placeholder="e.g. AI, Healthcare, Finance, Sustainability",
                help="What fields or industries interest you?"
            )
            
        experience = st.slider(
            "Years of experience 📈", 
            min_value=0, 
            max_value=30, 
            value=default_exp,
            help="Include all relevant professional experience"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Generate Career Guidance")

with tab2:
    if 'results' not in st.session_state:
        st.info("Complete the form in the Career Finder tab to see your personalized results here.")
    else:
        results = st.session_state.results
        
        # Success header
        st.markdown("<div class='success-card'>", unsafe_allow_html=True)
        st.markdown("### 🎉 Your Enhanced Career Guidance")
        
        # Display enhanced features
        enhanced_features = results.get("enhanced_features", {})
        if enhanced_features:
            features_text = []
            if enhanced_features.get("personality_inference"):
                features_text.append("**Personality-Based Matching**")
            if enhanced_features.get("lateral_paths"):
                features_text.append("**Vertical & Lateral Paths**")
            if enhanced_features.get("adaptive_planning"):
                features_text.append("**Adaptive Action Plan**")
            
            st.markdown(f"✨ {' • '.join(features_text)}")
        
        # Display personality profile if available
        personality_profile = results.get("role_fit", {}).get("personality_profile", {})
        if personality_profile:
            st.markdown(f"**Your Profile:** {', '.join(personality_profile.get('personality_traits', []))} | "
                       f"Work Style: {personality_profile.get('work_style', 'N/A')} | "
                       f"Environment: {personality_profile.get('preferred_environment', 'N/A')}")
        
        st.markdown(f"Based on **{len(results['role_fit']['recommended_roles'])}** recommended roles and **{len(results['career_path']['career_paths'])}** career paths")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Results in columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>💼 Recommended Roles</div>", unsafe_allow_html=True)
            roles = results.get("role_fit", {}).get("recommended_roles", [])
            if roles:
                for role in roles:
                    st.markdown(f"<div class='list-item'>👉 {role}</div>", unsafe_allow_html=True)
            else:
                st.warning("No roles found. Try adding more specific skills and interests.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🎯 Career Paths</div>", unsafe_allow_html=True)
            
            # Display vertical and lateral paths separately if available
            vertical_paths = results.get("career_path", {}).get("vertical_paths", [])
            lateral_paths = results.get("career_path", {}).get("lateral_paths", [])
            
            if vertical_paths or lateral_paths:
                if vertical_paths:
                    st.markdown("**📈 Vertical Growth Paths:**")
                    for path in vertical_paths:
                        st.markdown(f"<div class='list-item'>⬆️ {path}</div>", unsafe_allow_html=True)
                
                if lateral_paths:
                    st.markdown("**↔️ Lateral Transition Paths:**")
                    for path in lateral_paths:
                        st.markdown(f"<div class='list-item'>� {path}</div>", unsafe_allow_html=True)
            else:
                # Fallback to combined paths
                paths = results.get("career_path", {}).get("career_paths", [])
                if paths:
                    for path in paths:
                        st.markdown(f"<div class='list-item'>�🛣️ {path}</div>", unsafe_allow_html=True)
                else:
                    st.warning("No career paths found.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>❗ Skill Gaps to Address</div>", unsafe_allow_html=True)
            skill_gaps = results.get("action_plan", {}).get("skill_gaps", [])
            if skill_gaps and any(gap.strip() for gap in skill_gaps):
                for gap in skill_gaps:
                    if gap and gap.strip().lower() not in ["none", "undefined"]:
                        st.markdown(f"<div class='list-item'>🔍 {gap}</div>", unsafe_allow_html=True)
            else:
                st.info("No significant skill gaps identified. You seem well-prepared!")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Progress Tracking Section
            progress_tracker = results.get("action_plan", {}).get("progress_tracker", {})
            if progress_tracker:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>📊 Progress Tracking</div>", unsafe_allow_html=True)
                
                total_skills = progress_tracker.get("total_skills_needed", 0)
                completed_skills = progress_tracker.get("skills_completed", 0)
                
                if total_skills > 0:
                    progress_percentage = (completed_skills / total_skills) * 100
                    st.progress(progress_percentage / 100)
                    st.markdown(f"**Progress:** {completed_skills}/{total_skills} skills ({progress_percentage:.1f}%)")
                else:
                    st.markdown("**Ready to start your journey!**")
                
                st.markdown(f"*Last updated: {progress_tracker.get('last_updated', 'N/A')}*")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Action plan (full width)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📝 Your Personalized Action Plan</div>", unsafe_allow_html=True)
        action_plan = results.get("action_plan", {}).get("action_plan", "")
        if action_plan and action_plan.strip() and action_plan.strip().lower() not in ["no action plan generated.", "none", "undefined"]:
            st.markdown(action_plan)
        else:
            st.info("No action plan was generated. Please ensure your skills and interests are specific.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Export options
        st.markdown("<br>", unsafe_allow_html=True)
        export_col1, export_col2, export_col3 = st.columns([1, 1, 1])
        
        # Get user input from session state or history
        if 'history' in st.session_state and st.session_state.history:
            latest_input = st.session_state.history[0]
            input_for_export = {
                "skills": latest_input.get("skills", []),
                "interests": latest_input.get("interests", []),
                "experience": latest_input.get("experience", 0)
            }
        else:
            input_for_export = {
                "skills": [],
                "interests": [],
                "experience": 0
            }
            
        with export_col1:
            if st.button("📝 Export as Markdown"):
                markdown_content = format_results_as_markdown(results, input_for_export)
                st.download_button(
                    label="Download Markdown",
                    data=markdown_content,
                    file_name=f"career_guidance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        with export_col2:
            if st.button("🔄 Export as JSON"):
                json_content = export_results_as_json(results, input_for_export)
                st.download_button(
                    label="Download JSON",
                    data=json_content,
                    file_name=f"career_guidance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        with export_col3:
            if st.button("💾 Save to History"):
                st.success("Results saved to your history!")
                # Add timestamp for when this was run
                timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M")
                st.session_state.results["timestamp"] = timestamp
                # Add to history
                st.balloons()

# Process form submission
if submitted:
    user_input = {
        "skills": [s.strip() for s in skills.split(",") if s.strip()],
        "interests": [i.strip() for i in interests.split(",") if i.strip()],
        "experience": int(experience)
    }
    
    if not user_input["skills"] or not user_input["interests"]:
        st.warning("Please enter at least one skill and one interest.")
    else:
        # Switch to results tab
        st.session_state.active_tab = "Results"
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Stage 1: Role fitting
            status_text.text("🔍 Analyzing your skills and interests...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            graph = build_career_graph()
            
            # Stage 2: Running the AI pipeline
            status_text.text("🤖 Running AI career analysis...")
            progress_bar.progress(30)
            time.sleep(0.5)
            
            results = graph.run(user_input)
            
            # Stage 3: Generating career paths
            status_text.text("🛣️ Mapping potential career paths...")
            progress_bar.progress(60)
            time.sleep(0.5)
            
            # Stage 4: Creating action plan
            status_text.text("📝 Creating your personalized action plan...")
            progress_bar.progress(90)
            time.sleep(0.5)
            
            # Complete
            progress_bar.progress(100)
            status_text.text("✅ Your career guidance is ready!")
            time.sleep(1)
            
            # Clear progress indicators
            status_text.empty()
            progress_bar.empty()
            
            # Store results in session state
            st.session_state.results = results
            
            # Store in history (simplified version)
            history_item = {
                "skills": user_input["skills"],
                "interests": user_input["interests"],
                "experience": user_input["experience"],
                "roles": results.get("role_fit", {}).get("recommended_roles", []),
                "paths": results.get("career_path", {}).get("career_paths", []),
                "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M")
            }
            
            # Add to history if not already there
            if 'history' not in st.session_state:
                st.session_state.history = []
            st.session_state.history.insert(0, history_item)
            
            # Limit history size
            if len(st.session_state.history) > 5:
                st.session_state.history = st.session_state.history[:5]
            
            # Switch to results tab
            st.rerun()
            
        except Exception as e:
            error_message = str(e)
            # Clear progress indicators
            status_text.empty()
            progress_bar.empty()
            
            if "API_KEY_INVALID" in error_message or "API key not valid" in error_message:
                st.error("🔑 **Invalid API Key!**")
                st.markdown("""
                **To fix this issue:**
                1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
                2. Sign in with your Google account
                3. Create a new API key
                4. Copy the new API key
                5. Edit the `.env` file in your project folder
                6. Replace `YOUR_GEMINI_API_KEY_HERE` with your new API key
                7. Save the file and refresh this page
                """)
                st.info("💡 **Tip:** Make sure your API key has access to the Gemini API and hasn't expired.")
            else:
                st.error(f"❌ **An error occurred:** {error_message}")
                st.info("Please check your internet connection and try again. If the problem persists, contact support.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>© 2025 VishCraft Career Guidance • Powered by Gemini AI</div>", 
    unsafe_allow_html=True
)
