import streamlit as st
from career_graph import build_career_graph
import json
import time
from datetime import datetime
import os
from export_utils import export_results_as_json, format_results_as_markdown
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import re

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
        st.warning(f"CSS file {file_name} not found.")

# Apply enhanced CSS
local_css("assets/enhanced_style.css")

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

# Helper functions
def generate_skill_categories(skills):
    # Mock skill categories for visualization
    categories = ["Technical", "Soft", "Domain", "Tools"]
    skill_data = []
    
    for skill in skills:
        category = random.choice(categories)
        level = random.randint(50, 100)
        skill_data.append({"Skill": skill, "Category": category, "Level": level})
    
    return pd.DataFrame(skill_data)

def create_skill_radar_chart(skill_df):
    if skill_df.empty:
        return None
        
    # Group by category and calculate average
    category_avg = skill_df.groupby('Category')['Level'].mean().reset_index()
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=category_avg['Level'].tolist() + [category_avg['Level'].tolist()[0]],
        theta=category_avg['Category'].tolist() + [category_avg['Category'].tolist()[0]],
        fill='toself',
        fillcolor='rgba(58, 113, 202, 0.2)',
        line=dict(color='#3a71ca', width=2),
        name='Your Skills'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

def create_progress_chart(total, completed):
    if total == 0:
        return None
        
    percentage = (completed / total) * 100
    
    fig = go.Figure()
    
    # Add progress bar
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=percentage,
        title={"text": "Skill Progress"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "#3a71ca"},
            'bgcolor': "white",
            'steps': [
                {'range': [0, 33], 'color': "#f1f5fd"},
                {'range': [33, 66], 'color': "#e7effd"},
                {'range': [66, 100], 'color': "#d4e4fc"}
            ],
        },
        number={'suffix': "%"}
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

def create_timeline_flowchart(action_plan_text):
    """
    Create a professional timeline flowchart from the action plan text
    Parse the markdown text to extract monthly milestones and create a visual representation
    """
    if not action_plan_text:
        return None
    
    # Extract monthly milestones using regex
    months_data = []
    month_pattern = r"(?:^|\n)(?:\#{1,3}\s*)?(?:Month|MONTH)\s*(\d{1,2})(?:\s*[-:])?\s*(.*?)(?=\n(?:\#{1,3}\s*)?(?:Month|MONTH)\s*\d{1,2}|\n\#{1,3}|\Z)"
    month_matches = re.finditer(month_pattern, action_plan_text, re.DOTALL | re.MULTILINE)
    
    for match in month_matches:
        month_num = int(match.group(1))
        if month_num <= 12:  # Ensure we only get months 1-12
            content = match.group(2).strip()
            # Extract the first sentence or bullet point as the title
            title_match = re.search(r'^([^\.•\n]+(?:\.[^\.•\n]+)?)', content)
            title = title_match.group(1).strip() if title_match else f"Month {month_num} Milestones"
            
            # Extract key tasks using bullet points
            tasks = []
            task_matches = re.finditer(r'(?:^|\n)(?:[-•*]\s*|\d+\.\s*)(.*?)(?=\n[-•*]|\n\d+\.|\Z)', content, re.DOTALL)
            for task_match in task_matches:
                task = task_match.group(1).strip()
                if task and len(task) > 3:  # Filter out very short tasks
                    # Truncate long tasks
                    if len(task) > 70:
                        task = task[:67] + "..."
                    tasks.append(task)
            
            # If no tasks were found, create a generic one
            if not tasks and title != f"Month {month_num} Milestones":
                tasks.append(title)
                title = f"Month {month_num}"
            
            # Limit to 3 most important tasks
            tasks = tasks[:3]
            
            months_data.append({
                "month": month_num,
                "title": title,
                "tasks": tasks
            })
    
    # If we couldn't parse any months, return None
    if not months_data:
        return None
    
    # Sort by month number
    months_data.sort(key=lambda x: x["month"])
    
    # Create a professional timeline flowchart
    fig = go.Figure()
    
    # Define a professional color palette
    colors = [
        "#1A365D",  # Dark blue
        "#2A6BAE",  # Medium blue
        "#3C8DBC",  # Light blue
        "#0E4D92",  # Royal blue
        "#4B86B4",  # Steel blue
        "#2E5984",  # Navy blue
        "#3E6990",  # Blue gray
        "#254E70",  # Dark slate blue
        "#1F3F66",  # Dark navy
        "#2C4770",  # Indigo blue
        "#2B5D7D",  # Teal blue
        "#346888"   # Slate blue
    ]
    
    # Main timeline axis
    fig.add_trace(go.Scatter(
        x=list(range(1, len(months_data) + 1)),
        y=[0] * len(months_data),
        mode="lines+markers",
        line=dict(color="#0A2463", width=3),
        marker=dict(size=20, color="#0A2463", symbol="circle"),
        hoverinfo="none",
        showlegend=False
    ))
    
    # Add month points and annotations
    for i, month_data in enumerate(months_data):
        month_num = month_data["month"]
        title = month_data["title"]
        tasks = month_data["tasks"]
        
        # Month number labels
        fig.add_annotation(
            x=i+1,
            y=0,
            text=f"{month_num}",
            font=dict(size=12, color="white"),
            showarrow=False
        )
        
        # Month title above the timeline
        fig.add_annotation(
            x=i+1,
            y=0.3,
            text=f"<b>{title}</b>",
            font=dict(size=12, color=colors[i % len(colors)]),
            showarrow=False,
            align="center",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor=colors[i % len(colors)],
            borderwidth=1,
            borderpad=4,
            width=200
        )
        
        # Tasks below the timeline
        task_y = -0.3
        for task in tasks:
            fig.add_annotation(
                x=i+1,
                y=task_y,
                text=f"• {task}",
                font=dict(size=10),
                showarrow=False,
                align="left",
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="#D3D3D3",
                borderwidth=1,
                borderpad=3,
                width=180
            )
            task_y -= 0.2
    
    # Layout configuration
    fig.update_layout(
        title=dict(
            text="<b>12-Month Career Development Timeline</b>",
            font=dict(size=18, color="#0A2463"),
            x=0.5
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=500,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, len(months_data) + 1]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, 1]
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        shapes=[
            # Horizontal line for timeline
            dict(
                type="line",
                xref="x",
                yref="y",
                x0=0.5,
                y0=0,
                x1=len(months_data) + 0.5,
                y1=0,
                line=dict(color="#0A2463", width=3)
            )
        ]
    )
    
    return fig

# Sidebar
with st.sidebar:
    try:
        st.image("assets/brain_icon.png", width=100)
    except:
        st.image("https://img.icons8.com/fluency/96/000000/brain.png", width=100)
    
    st.markdown("<div class='sidebar-title'>VishCraft AI Career Guidance</div>", unsafe_allow_html=True)
    
    st.markdown("### How It Works")
    st.markdown("""
    <div class="info-card">
        <p><b>1. RoleFitAssistant</b> 👔</p>
        <p style="font-size: 0.9rem;">Analyzes your skills, interests, and infers personality traits to suggest suitable roles</p>
        <p><b>2. CareerPathAssistant</b> 🛣️</p>
        <p style="font-size: 0.9rem;">Maps both vertical growth and lateral transition paths</p>
        <p><b>3. ActionPlanAssistant</b> 📝</p>
        <p style="font-size: 0.9rem;">Creates a personalized adaptive plan with skill gap analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Tips for Best Results")
    st.markdown("""
    <div class="info-card">
        <p>✅ Be specific with technical skills</p>
        <p>✅ Include soft skills like communication</p>
        <p>✅ Add diverse interests for broader options</p>
        <p>✅ Accurately report your experience level</p>
    </div>
    """, unsafe_allow_html=True)
    
    # History feature in sidebar
    st.markdown("### 📋 Previous Searches")
    
    # Load history from session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # Display history
    if not st.session_state.history:
        st.info("Your search history will appear here")
    else:
        for idx, item in enumerate(st.session_state.history):
            st.markdown(
                f"""<div class="history-item" onclick="alert('Click the button below to load this search')">
                    <b>{', '.join(item['skills'][:2])}{'' if len(item['skills']) <= 2 else '...'}</b>
                    <p style="font-size: 0.8rem; margin: 0;">
                        {len(item['roles'])} roles • {item['timestamp']}
                    </p>
                </div>""", 
                unsafe_allow_html=True
            )
            if st.button(f"Load Search #{idx+1}", key=f"hist_{idx}", help="Reload this previous search"):
                st.session_state.load_item = item
                st.rerun()

    # Add a version info at the bottom
    st.markdown("<div class='footer'>Version 2.0 • July 2025</div>", unsafe_allow_html=True)

# Main content
st.markdown("<h1 class='main-header'>VishCraft AI Career Guidance</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Discover your ideal career path with AI-powered personality analysis and adaptive planning</p>", unsafe_allow_html=True)

# Create tabs with enhanced styling
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Career Finder", "📊 Results", "📈 Progress Tracker", "❓ Help"])

with tab1:
    st.markdown("<div class='section-title'>🎯 Tell us about yourself</div>", unsafe_allow_html=True)
    st.markdown("Enter your skills, interests, and experience to get personalized career recommendations with personality insights")
    
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
        
        col3, col4 = st.columns(2)
        with col3:
            experience = st.slider(
                "Years of experience 📈", 
                min_value=0, 
                max_value=30, 
                value=default_exp,
                help="Include all relevant professional experience"
            )
        
        with col4:
            st.markdown("""
            <div style="background-color: rgba(58, 113, 202, 0.1); padding: 0.8rem; border-radius: 8px;">
                <p style="margin: 0;"><strong>✨ Enhanced with:</strong></p>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                    <span class="feature-badge">Personality Analysis</span>
                    <span class="feature-badge">Career Mapping</span>
                    <span class="feature-badge">Adaptive Planning</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Generate Career Guidance")
    
    # Example showcase
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>💡 Example Profiles</div>", unsafe_allow_html=True)
    
    example_col1, example_col2, example_col3 = st.columns(3)
    
    with example_col1:
        st.markdown("""
        <div style="background-color: #f1f8e9; padding: 1rem; border-radius: 8px; height: 100%;">
            <h4 style="color: #2e7d32;">💻 Tech Profile</h4>
            <p><strong>Skills:</strong> Python, JavaScript, Machine Learning, UI/UX, Communication</p>
            <p><strong>Interests:</strong> AI, Mobile Apps, Cloud Computing</p>
            <p><strong>Experience:</strong> 3 years</p>
        </div>
        """, unsafe_allow_html=True)
    
    with example_col2:
        st.markdown("""
        <div style="background-color: #e1f5fe; padding: 1rem; border-radius: 8px; height: 100%;">
            <h4 style="color: #0277bd;">🏥 Healthcare Profile</h4>
            <p><strong>Skills:</strong> Patient Care, Medical Terminology, Clinical Research, Leadership</p>
            <p><strong>Interests:</strong> Healthcare Tech, Preventive Medicine, Biotechnology</p>
            <p><strong>Experience:</strong> 5 years</p>
        </div>
        """, unsafe_allow_html=True)
    
    with example_col3:
        st.markdown("""
        <div style="background-color: #fff8e1; padding: 1rem; border-radius: 8px; height: 100%;">
            <h4 style="color: #ff8f00;">💼 Business Profile</h4>
            <p><strong>Skills:</strong> Marketing, Project Management, Data Analysis, Public Speaking</p>
            <p><strong>Interests:</strong> Digital Marketing, E-commerce, Entrepreneurship</p>
            <p><strong>Experience:</strong> 2 years</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    if 'results' not in st.session_state:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
            <img src="https://img.icons8.com/fluency/96/000000/search.png" width="80" style="margin-bottom: 1rem;">
            <h3>Complete the form to see your results</h3>
            <p>Go to the Career Finder tab and enter your skills, interests, and experience to get personalized career guidance.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        results = st.session_state.results
        
        # Success header with enhanced styling
        st.markdown("""
        <div class='success-card' style="background: linear-gradient(135deg, #f1f8e9, #e8f5e9); border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
            <h2 style="margin-top: 0; display: flex; align-items: center;">
                <span style="background-color: #22bb33; color: white; border-radius: 50%; width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; margin-right: 10px;">✓</span>
                Your Enhanced Career Guidance
            </h2>
        """, unsafe_allow_html=True)
        
        # Display enhanced features with badge styling
        enhanced_features = results.get("enhanced_features", {})
        if enhanced_features:
            st.markdown("<div style='display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
            
            if enhanced_features.get("personality_inference"):
                st.markdown("<span class='feature-badge' style='background-color: #8559da;'>✨ Personality-Based Matching</span>", unsafe_allow_html=True)
            if enhanced_features.get("lateral_paths"):
                st.markdown("<span class='feature-badge' style='background-color: #3a71ca;'>🔄 Vertical & Lateral Paths</span>", unsafe_allow_html=True)
            if enhanced_features.get("adaptive_planning"):
                st.markdown("<span class='feature-badge' style='background-color: #22bb33;'>📝 Adaptive Action Plan</span>", unsafe_allow_html=True)
            if enhanced_features.get("monetization_ready"):
                st.markdown("<span class='feature-badge' style='background-color: #ff7043;'>🔒 Premium Format</span>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display personality profile with enhanced styling
        personality_profile = results.get("role_fit", {}).get("personality_profile", {})
        if personality_profile:
            st.markdown("""
            <div style="background-color: rgba(58, 113, 202, 0.1); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <h4 style="margin-top: 0;">🧠 Your Personality Profile</h4>
                <p><strong>Traits:</strong> {traits}</p>
                <p><strong>Work Style:</strong> {work_style}</p>
                <p><strong>Preferred Environment:</strong> {environment}</p>
            </div>
            """.format(
                traits=', '.join(personality_profile.get('personality_traits', [])),
                work_style=personality_profile.get('work_style', 'N/A'),
                environment=personality_profile.get('preferred_environment', 'N/A')
            ), unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Results in columns with enhanced styling
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Recommended Roles section
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>💼 Recommended Roles</div>", unsafe_allow_html=True)
            roles = results.get("role_fit", {}).get("recommended_roles", [])
            if roles:
                for role in roles:
                    st.markdown(f"<div class='list-item'>👉 {role}</div>", unsafe_allow_html=True)
            else:
                st.warning("No roles found. Try adding more specific skills and interests.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Career Paths section with enhanced styling
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🛣️ Career Paths</div>", unsafe_allow_html=True)
            
            # Display vertical and lateral paths separately with different styling
            vertical_paths = results.get("career_path", {}).get("vertical_paths", [])
            lateral_paths = results.get("career_path", {}).get("lateral_paths", [])
            
            if vertical_paths or lateral_paths:
                if vertical_paths:
                    st.markdown("**📈 Vertical Growth Paths:**")
                    for path in vertical_paths:
                        st.markdown(f"<div class='vertical-path-item'>⬆️ {path}</div>", unsafe_allow_html=True)
                
                if lateral_paths:
                    st.markdown("**↔️ Lateral Transition Paths:**")
                    for path in lateral_paths:
                        st.markdown(f"<div class='lateral-path-item'>↔️ {path}</div>", unsafe_allow_html=True)
            else:
                # Fallback to combined paths
                paths = results.get("career_path", {}).get("career_paths", [])
                if paths:
                    for path in paths:
                        st.markdown(f"<div class='list-item'>🛣️ {path}</div>", unsafe_allow_html=True)
                else:
                    st.warning("No career paths found.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            # Skill Gaps section with enhanced styling
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🔍 Skill Gaps to Address</div>", unsafe_allow_html=True)
            skill_gaps = results.get("action_plan", {}).get("skill_gaps", [])
            if skill_gaps and any(gap.strip() for gap in skill_gaps):
                for gap in skill_gaps:
                    if gap and gap.strip().lower() not in ["none", "undefined"]:
                        st.markdown(f"<div class='skill-gap-item'>🔍 {gap}</div>", unsafe_allow_html=True)
            else:
                st.info("No significant skill gaps identified. You seem well-prepared!")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Progress Tracking Section with enhanced visualization
            progress_tracker = results.get("action_plan", {}).get("progress_tracker", {})
            if progress_tracker:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>📊 Progress Tracking</div>", unsafe_allow_html=True)
                
                total_skills = progress_tracker.get("total_skills_needed", 0)
                completed_skills = progress_tracker.get("skills_completed", 0)
                
                # Create a visual progress chart
                progress_chart = create_progress_chart(total_skills, completed_skills)
                if progress_chart:
                    st.plotly_chart(progress_chart, use_container_width=True)
                else:
                    if total_skills > 0:
                        progress_percentage = (completed_skills / total_skills) * 100
                        st.progress(progress_percentage / 100)
                        st.markdown(f"**Progress:** {completed_skills}/{total_skills} skills ({progress_percentage:.1f}%)")
                    else:
                        st.markdown("**Ready to start your journey!**")
                
                st.markdown(f"*Last updated: {progress_tracker.get('last_updated', 'N/A')}*")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Add a visualization for skills
            if 'skills' in st.session_state:
                skills_list = st.session_state.get('skills', [])
                if skills_list:
                    # Create skill visualization
                    skill_df = generate_skill_categories(skills_list)
                    skill_chart = create_skill_radar_chart(skill_df)
                    
                    if skill_chart:
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-title'>📊 Skills Overview</div>", unsafe_allow_html=True)
                        st.plotly_chart(skill_chart, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
        
        # Action plan (full width) with enhanced styling
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📝 Your Personalized Action Plan</div>", unsafe_allow_html=True)
        action_plan = results.get("action_plan", {}).get("action_plan", "")
        if action_plan and action_plan.strip() and action_plan.strip().lower() not in ["no action plan generated.", "none", "undefined"]:
            # Generate the timeline flowchart
            timeline_chart = create_timeline_flowchart(action_plan)
            if timeline_chart:
                st.markdown("<div class='timeline-wrapper'>", unsafe_allow_html=True)
                st.plotly_chart(timeline_chart, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Add a collapsible section for the full text version
                with st.expander("View detailed action plan"):
                    st.markdown(action_plan)
            else:
                # Fallback to regular text if parsing fails
                st.markdown(action_plan)
        else:
            st.info("No action plan was generated. Please ensure your skills and interests are specific.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Export options with enhanced styling
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
            if st.button("📝 Export as Markdown", help="Download your results as a Markdown file"):
                markdown_content = format_results_as_markdown(results, input_for_export)
                st.download_button(
                    label="Download Markdown",
                    data=markdown_content,
                    file_name=f"career_guidance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        with export_col2:
            if st.button("🔄 Export as JSON", help="Download your results as a JSON file"):
                json_content = export_results_as_json(results, input_for_export)
                st.download_button(
                    label="Download JSON",
                    data=json_content,
                    file_name=f"career_guidance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        with export_col3:
            if st.button("💾 Save to History", help="Save this result to your search history"):
                st.success("Results saved to your history!")
                # Add timestamp for when this was run
                timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M")
                st.session_state.results["timestamp"] = timestamp
                # Add to history
                st.balloons()

with tab3:
    if 'results' not in st.session_state:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
            <img src="https://img.icons8.com/fluency/96/000000/combo-chart.png" width="80" style="margin-bottom: 1rem;">
            <h3>Track Your Progress</h3>
            <p>Once you generate your career guidance, you can track your skill development progress here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        results = st.session_state.results
        skill_gaps = results.get("action_plan", {}).get("skill_gaps", [])
        
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📈 Progress Tracking Dashboard</div>", unsafe_allow_html=True)
        st.markdown("Track your skill development progress and update your career action plan")
        
        # Store completed skills in session state if not already there
        if 'completed_skills' not in st.session_state:
            st.session_state.completed_skills = []
        
        if skill_gaps and any(gap.strip() for gap in skill_gaps):
            st.markdown("### Skills to Develop")
            
            # Create a form for tracking skill progress
            with st.form("progress_form"):
                progress_data = []
                
                for i, gap in enumerate(skill_gaps):
                    if gap and gap.strip().lower() not in ["none", "undefined"]:
                        is_completed = gap in st.session_state.completed_skills
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"**{gap}**")
                        
                        with col2:
                            # Use a checkbox to mark skills as completed
                            completed = st.checkbox("Completed", value=is_completed, key=f"skill_{i}")
                            if completed:
                                progress_data.append((gap, True))
                            else:
                                progress_data.append((gap, False))
                
                st.markdown("<br>", unsafe_allow_html=True)
                update_submitted = st.form_submit_button("📊 Update Progress")
                
                if update_submitted:
                    # Update completed skills in session state
                    st.session_state.completed_skills = [skill for skill, completed in progress_data if completed]
                    
                    # Update progress tracker in results
                    progress_tracker = results.get("action_plan", {}).get("progress_tracker", {})
                    if progress_tracker:
                        progress_tracker["skills_completed"] = len(st.session_state.completed_skills)
                        progress_tracker["completion_percentage"] = (len(st.session_state.completed_skills) / max(len(skill_gaps), 1)) * 100
                        progress_tracker["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Update the results
                        st.session_state.results["action_plan"]["progress_tracker"] = progress_tracker
                        
                        st.success("Progress updated successfully!")
                        st.experimental_rerun()
            
            # Display visual progress
            total = len(skill_gaps)
            completed = len(st.session_state.completed_skills)
            
            if total > 0:
                percentage = (completed / total) * 100
                
                # Display progress bar
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### Overall Progress")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="skill-progress-container">
                        <div class="skill-progress-bar" style="width: {percentage}%;"></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{percentage:.1f}%** completed")
                
                # Create a visual progress chart
                progress_chart = create_progress_chart(total, completed)
                if progress_chart:
                    st.plotly_chart(progress_chart, use_container_width=True)
                
                # Add some motivational message based on progress
                if percentage < 25:
                    st.markdown("""
                    <div class="info-card">
                        <h4>🌱 Getting Started</h4>
                        <p>You're at the beginning of your journey. Take one skill at a time and celebrate small wins!</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif percentage < 50:
                    st.markdown("""
                    <div class="info-card">
                        <h4>🚀 Building Momentum</h4>
                        <p>You're making good progress! Keep up the consistent effort and you'll see results.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif percentage < 75:
                    st.markdown("""
                    <div class="info-card">
                        <h4>💪 Strong Progress</h4>
                        <p>You've completed a significant portion of your skill goals. You're well on your way to success!</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="success-card">
                        <h4>🏆 Nearly There!</h4>
                        <p>Impressive progress! You're close to mastering all the skills needed for your career path.</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Advanced feature: Update action plan based on progress
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Update Action Plan")
            st.markdown("As you complete skills, you can get an updated action plan that reflects your progress")
            
            if st.button("🔄 Generate Updated Action Plan"):
                with st.spinner("Updating your action plan based on progress..."):
                    try:
                        # Prepare input for update_progress
                        remaining_skills = [gap for gap in skill_gaps if gap not in st.session_state.completed_skills]
                        current_plan = results.get("action_plan", {}).get("action_plan", "")
                        career_paths = results.get("career_path", {}).get("career_paths", [])
                        
                        update_input = {
                            "completed_skills": st.session_state.completed_skills,
                            "remaining_skills": remaining_skills,
                            "current_plan": current_plan,
                            "career_paths": career_paths
                        }
                        
                        # Get a new instance of ActionPlanAssistant
                        from action_plan_assistant import ActionPlanAssistant
                        action_plan_assistant = ActionPlanAssistant()
                        
                        # Call update_progress
                        update_result = action_plan_assistant.update_progress(update_input)
                        
                        # Display the updated plan
                        st.markdown("<div class='success-card'>", unsafe_allow_html=True)
                        st.markdown("<div class='section-title'>📝 Your Updated Action Plan</div>", unsafe_allow_html=True)
                        st.markdown(update_result.get("updated_plan", "No updated plan generated."))
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Display new recommendations
                        new_recommendations = update_result.get("new_recommendations", [])
                        if new_recommendations:
                            st.markdown("<div class='card'>", unsafe_allow_html=True)
                            st.markdown("<div class='section-title'>✨ New Recommendations</div>", unsafe_allow_html=True)
                            for rec in new_recommendations:
                                st.markdown(f"<div class='list-item'>👉 {rec}</div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Display motivational message
                        if "motivation_message" in update_result:
                            st.info(update_result["motivation_message"])
                        
                    except Exception as e:
                        st.error(f"Error updating action plan: {str(e)}")
        else:
            st.info("No skill gaps identified to track. Generate a career guidance first with specific skills and interests.")
        
        st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>❓ Frequently Asked Questions</div>", unsafe_allow_html=True)
    
    # Create expandable sections for FAQs
    with st.expander("How does the personality analysis work?"):
        st.markdown("""
        Our system analyzes your skills and interests to infer key personality traits using advanced AI models.
        
        The analysis is based on:
        - Technical skills (indicating cognitive preferences)
        - Soft skills (revealing interpersonal styles)
        - Interests (showing motivational factors)
        
        This information helps match you to roles that fit not just your skills, but your natural work style and preferences.
        """)
    
    with st.expander("What's the difference between vertical and lateral career paths?"):
        st.markdown("""
        **Vertical Career Paths** represent traditional upward progression:
        - Moving up the hierarchy in your field
        - Increasing responsibility and seniority
        - Example: Junior Developer → Senior Developer → Development Manager
        
        **Lateral Career Paths** represent sideways moves to related roles:
        - Moving to adjacent fields using transferable skills
        - Exploring different industries with similar skill requirements
        - Example: Data Analyst → Business Analyst → Product Manager
        """)
    
    with st.expander("How accurate is the skill gap analysis?"):
        st.markdown("""
        The skill gap analysis identifies the most critical skills you need to develop based on:
        
        1. Your current skills
        2. The requirements of your target career paths
        3. Industry standards and trends
        
        While the analysis is powered by advanced AI, it's intended as a starting point. Consider validating specific skills with job postings or industry professionals in your target field.
        """)
    
    with st.expander("Can I save or export my results?"):
        st.markdown("""
        Yes! You have several options:
        
        1. **Save to History**: Save your results to access later within this session
        2. **Export as Markdown**: Download a formatted document with all your results
        3. **Export as JSON**: Download your data in JSON format for other applications
        
        Your data is not stored on our servers after you close this application.
        """)
    
    with st.expander("How can I track my progress?"):
        st.markdown("""
        The Progress Tracker tab allows you to:
        
        1. Mark skills as completed
        2. Visualize your overall progress
        3. Generate updated action plans based on your progress
        
        This helps you adapt your learning journey as you develop new skills.
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Contact section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📞 Need Help?</div>", unsafe_allow_html=True)
    
    st.markdown("""
    If you have any questions or need assistance, please contact us:
    
    - **Email**: support@vishcraft.ai
    - **Website**: [www.vishcraft.ai](https://www.vishcraft.ai)
    - **Hours**: Monday-Friday, 9 AM - 5 PM EST
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Process form submission
if submitted:
    user_input = {
        "skills": [s.strip() for s in skills.split(",") if s.strip()],
        "interests": [i.strip() for i in interests.split(",") if i.strip()],
        "experience": int(experience)
    }
    
    # Store skills in session state for visualization
    st.session_state.skills = user_input["skills"]
    
    if not user_input["skills"] or not user_input["interests"]:
        st.warning("Please enter at least one skill and one interest.")
    else:
        # Switch to results tab
        st.session_state.active_tab = "Results"
        
        # Create progress bar with enhanced styling
        progress_placeholder = st.empty()
        status_text = st.empty()
        
        with progress_placeholder.container():
            progress_bar = st.progress(0)
        
        try:
            # Stage 1: Role fitting
            status_text.markdown("""
            <div style="text-align: center; padding: 1rem; background-color: var(--primary-light); border-radius: 8px;">
                <h3 style="margin: 0;">🔍 Analyzing your skills and personality...</h3>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(10)
            time.sleep(0.5)
            
            graph = build_career_graph()
            
            # Stage 2: Running the AI pipeline
            status_text.markdown("""
            <div style="text-align: center; padding: 1rem; background-color: var(--primary-light); border-radius: 8px;">
                <h3 style="margin: 0;">🤖 Running AI career analysis...</h3>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(30)
            time.sleep(0.5)
            
            results = graph.run(user_input)
            
            # Stage 3: Generating career paths
            status_text.markdown("""
            <div style="text-align: center; padding: 1rem; background-color: var(--primary-light); border-radius: 8px;">
                <h3 style="margin: 0;">🛣️ Mapping potential career paths...</h3>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(60)
            time.sleep(0.5)
            
            # Stage 4: Creating action plan
            status_text.markdown("""
            <div style="text-align: center; padding: 1rem; background-color: var(--primary-light); border-radius: 8px;">
                <h3 style="margin: 0;">📝 Creating your personalized action plan...</h3>
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(90)
            time.sleep(0.5)
            
            # Complete
            progress_bar.progress(100)
            status_text.markdown("""
            <div style="text-align: center; padding: 1rem; background-color: #f1f8e9; border-radius: 8px;">
                <h3 style="margin: 0; color: #22bb33;">✅ Your career guidance is ready!</h3>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
            
            # Clear progress indicators
            status_text.empty()
            progress_placeholder.empty()
            
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
            progress_placeholder.empty()
            
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

# Footer with enhanced styling
st.markdown("""
<div class="footer">
    <p>© 2025 VishCraft Career Guidance • Powered by Gemini AI</p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem;">
        <a href="#" style="color: var(--primary); text-decoration: none; margin: 0 0.5rem;">Privacy Policy</a> • 
        <a href="#" style="color: var(--primary); text-decoration: none; margin: 0 0.5rem;">Terms of Service</a> • 
        <a href="#" style="color: var(--primary); text-decoration: none; margin: 0 0.5rem;">About Us</a>
    </p>
</div>
""", unsafe_allow_html=True)
