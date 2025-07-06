
import streamlit as st
from career_graph import build_career_graph

st.set_page_config(page_title="Career Guidance Tool", layout="centered")
st.title(":sparkles: Career Guidance Tool with AI Agents :sparkles:")
st.markdown("""
This tool helps you discover suitable roles, career paths, and a personalized action plan based on your skills, interests, and experience. Powered by multi-agent AI orchestration.
""")

with st.form("career_form"):
    col1, col2 = st.columns(2)
    with col1:
        skills = st.text_area("Enter your skills (comma separated)", placeholder="e.g. Python, Data Analysis, Communication")
    with col2:
        interests = st.text_area("Enter your interests (comma separated)", placeholder="e.g. AI, Healthcare, Finance")
    experience = st.slider("Years of experience", min_value=0, max_value=50, value=1)
    submitted = st.form_submit_button(":rocket: Get Career Guidance")

if submitted:
    user_input = {
        "skills": [s.strip() for s in skills.split(",") if s.strip()],
        "interests": [i.strip() for i in interests.split(",") if i.strip()],
        "experience": int(experience)
    }
    if not user_input["skills"] or not user_input["interests"]:
        st.warning("Please enter at least one skill and one interest.")
    else:
        graph = build_career_graph()
        with st.spinner("Running AI agents and generating your personalized guidance..."):
            try:
                results = graph.run(user_input)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                results = None
        if results:
            st.success(":tada: Here are your personalized career recommendations:")
            st.markdown("---")
            st.subheader(":briefcase: Recommended Roles")
            roles = results.get("role_fit", {}).get("recommended_roles", [])
            if roles:
                st.write("\n".join(f"- {role}" for role in roles))
            else:
                st.write("No roles found.")
            st.subheader(":dart: Career Paths")
            paths = results.get("career_path", {}).get("career_paths", [])
            if paths:
                st.write("\n".join(f"- {path}" for path in paths))
            else:
                st.write("No career paths found.")
            st.subheader(":bulb: Action Plan")
            action_plan = results.get("action_plan", {}).get("action_plan", "")
            if action_plan and action_plan.strip() and action_plan.strip().lower() not in ["no action plan generated.", "none", "undefined"]:
                st.markdown(action_plan, unsafe_allow_html=True)
            else:
                st.info("No action plan was generated. Please ensure your skills and interests are specific and relevant to your chosen career paths.")

            st.subheader(":triangular_flag_on_post: Skill Gaps")
            skill_gaps = results.get("action_plan", {}).get("skill_gaps", [])
            if skill_gaps and any(gap.strip() for gap in skill_gaps):
                st.write("\n".join(f"- {gap}" for gap in skill_gaps if gap and gap.strip().lower() not in ["none", "undefined"]))
            else:
                st.info("No significant skill gaps identified. You may already be well-prepared, or try providing more detailed skills and interests.")
