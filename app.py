import streamlit as st
from planner import generate_fitness_plan, modify_fitness_plan
from supabase_db import (
    register_user, login_user,
    save_profile, get_profile,
    save_plan, get_current_plan,
    log_progress, get_progress
)
import pandas as pd

st.set_page_config(
    page_title="FitForge",
    page_icon="FitForge.jpeg",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background-color: #0a0a0f; }
    .header-card {
        background: linear-gradient(135deg, #ff4b4b, #ff8c00, #ff4b4b);
        background-size: 200% 200%;
        animation: gradientShift 3s ease infinite;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(255, 75, 75, 0.3);
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .header-card h1 { font-size: 2.5rem; font-weight: 700; margin: 0; }
    .header-card p { font-size: 1.1rem; margin: 10px 0 0; opacity: 0.9; }
    .plan-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        padding: 30px;
        border-radius: 20px;
        border-left: 5px solid #ff4b4b;
        color: #e0e0e0;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .plan-card h3 { color: #ff4b4b; font-size: 1.3rem; margin-bottom: 15px; }
    .stButton>button {
        background: linear-gradient(135deg, #ff4b4b, #ff8c00);
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4);
    }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        padding: 15px;
        border-radius: 15px;
        border-bottom: 3px solid #ff4b4b;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    [data-testid="stSidebar"] { background-color: #0d0d1a; }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a2e;
        border-radius: 10px;
        padding: 5px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff4b4b, #ff8c00) !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==================
# SESSION STATE INIT
# ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "name" not in st.session_state:
    st.session_state.name = None

# ==================
# NOT LOGGED IN
# ==================
if not st.session_state.logged_in:

    st.markdown("""
        <div class="header-card">
            <h1>FitForge</h1>
            <p>Your Personal AI Fitness Coach</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not login_username or not login_password:
                st.error("Please fill all fields!")
            else:
                with st.spinner("Logging in..."):
                    success, message, user = login_user(
                        login_username, login_password
                    )

                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.name = user["name"]

                    # Default values set pannudu
                    if "age" not in st.session_state:
                        st.session_state.age = 25
                    if "current_weight" not in st.session_state:
                        st.session_state.current_weight = 70
                    if "target_weight" not in st.session_state:
                        st.session_state.target_weight = 65
                    if "height" not in st.session_state:
                        st.session_state.height = 170
                    if "goal" not in st.session_state:
                        st.session_state.goal = "Weight Loss"
                    if "activity_level" not in st.session_state:
                        st.session_state.activity_level = "Sedentary (No exercise)"
                    if "available_time" not in st.session_state:
                        st.session_state.available_time = 45

                    # Plan load pannudu
                    existing_plan = get_current_plan(login_username)
                    if existing_plan:
                        st.session_state.plan = existing_plan

                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(message)

    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Username", key="reg_username")
        new_name = st.text_input("Full Name", key="reg_name")
        new_password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Register"):
            if not new_username or not new_name or not new_password:
                st.error("Please fill all fields!")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                with st.spinner("Creating account..."):
                    success, message = register_user(
                        new_username, new_name, new_password
                    )
                if success:
                    st.success(message + " Please login!")
                else:
                    st.error(message)

# ==================
# LOGGED IN
# ==================
if st.session_state.logged_in:

    username = st.session_state.username
    name = st.session_state.name

    # Profile load pannudu — every page load la
    if "profile_loaded" not in st.session_state:
        profile = get_profile(username)
        if profile:
            st.session_state.age = int(profile.get("age") or 25)
            st.session_state.current_weight = int(profile.get("current_weight") or 70)
            st.session_state.target_weight = int(profile.get("target_weight") or 65)
            st.session_state.height = int(profile.get("height") or 170)
            st.session_state.goal = profile.get("goal") or "Weight Loss"
            st.session_state.activity_level = profile.get("activity_level") or "Sedentary (No exercise)"
            st.session_state.available_time = int(profile.get("available_time") or 45)
        st.session_state.profile_loaded = True

    # Sidebar
    st.sidebar.markdown(f"""
        <div style="
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, #ff4b4b, #ff8c00);
            border-radius: 15px;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(255,75,75,0.3);
        ">
            <h2 style="margin:0;font-size:1.8rem;">FitForge</h2>
            <p style="margin:8px 0 0;opacity:0.9;">Welcome, {name}!</p>
        </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.selectbox(
        "Navigation",
        ["Generate Plan", "Track Progress", "View History"]
    )
    st.sidebar.markdown("---")
    st.sidebar.info("Tip: Generate your plan first then track daily progress!")

    # ==================
    # PAGE 1 — Generate Plan
    # ==================
    if page == "Generate Plan":

        st.markdown("""
            <div class="header-card">
                <h1>AI Fitness Planner</h1>
                <p>Get your personalized workout and diet plan in seconds!</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("fitness_form"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Personal Details")
                st.number_input("Age",
                    min_value=10, max_value=80,
                    key="age")
                st.number_input("Current Weight (kg)",
                    min_value=30, max_value=200,
                    key="current_weight")
                st.number_input("Target Weight (kg)",
                    min_value=30, max_value=200,
                    key="target_weight")
                st.number_input("Height (cm)",
                    min_value=100, max_value=250,
                    key="height")

            with col2:
                st.subheader("Fitness Goals")
                goals_list = [
                    "Weight Loss", "Weight Gain", "Muscle Gain",
                    "Stay Fit", "Increase Stamina",
                    "Improve Flexibility", "Fix Posture", "Sports Fitness"
                ]
                st.selectbox("Your Goal",
                    goals_list,
                    key="goal")

                activity_list = [
                    "Sedentary (No exercise)",
                    "Lightly Active (1-2 days/week)",
                    "Moderately Active (3-4 days/week)",
                    "Very Active (5+ days/week)"
                ]
                st.selectbox("Activity Level",
                    activity_list,
                    key="activity_level")

                st.slider(
                    "Available Time (minutes/day)",
                    min_value=15, max_value=120,
                    key="available_time")

            submitted = st.form_submit_button("Generate My Plan")

        if submitted:
            with st.spinner("AI generating your personalized plan..."):
                plan, bmi, bmi_category = generate_fitness_plan(
                    st.session_state.age,
                    st.session_state.current_weight,
                    st.session_state.target_weight,
                    st.session_state.height,
                    st.session_state.goal,
                    st.session_state.activity_level,
                    st.session_state.available_time
                )
                st.session_state.plan = plan
                st.session_state.bmi = bmi
                st.session_state.bmi_category = bmi_category

                save_profile(
                    username,
                    st.session_state.age,
                    st.session_state.current_weight,
                    st.session_state.target_weight,
                    st.session_state.height,
                    st.session_state.goal,
                    st.session_state.activity_level,
                    st.session_state.available_time
                )
                save_plan(username, plan)
            st.toast("Plan generated successfully!", icon="✅")

        if "plan" in st.session_state and st.session_state.plan:

            bmi_val = st.session_state.get("bmi", 0)
            bmi_cat = st.session_state.get("bmi_category", "N/A")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Your BMI", bmi_val)
            with col2:
                st.metric("BMI Category", bmi_cat)
            with col3:
                if bmi_cat == "Normal weight":
                    st.metric("Status", "Healthy!")
                elif bmi_cat == "Underweight":
                    st.metric("Status", "Need to gain!")
                elif bmi_cat == "Overweight":
                    st.metric("Status", "Need to lose!")
                else:
                    st.metric("Status", "Take action!")

            if bmi_val:
                bmi_progress = min(bmi_val / 40, 1.0)
                st.progress(bmi_progress,
                    text=f"BMI: {bmi_val} — Healthy range: 18.5 - 24.9"
                )

            st.markdown("---")
            st.markdown("""
                <div class="plan-card">
                    <h3>Your Personalized Fitness Plan</h3>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.plan)

            st.markdown("---")
            st.subheader("Not comfortable with something?")
            feedback = st.text_input(
                "Tell AI what to change",
                placeholder="Ex: I can't do running, I have knee pain..."
            )

            if st.button("Modify My Plan"):
                if feedback:
                    with st.spinner("AI modifying your plan..."):
                        modified = modify_fitness_plan(
                            st.session_state.plan,
                            feedback
                        )
                        st.session_state.plan = modified
                        save_plan(username, modified)
                    st.toast("Plan modified!", icon="✅")
                    st.rerun()
                else:
                    st.warning("Please enter your feedback!")

    # ==================
    # PAGE 2 — Track Progress
    # ==================
    elif page == "Track Progress":

        st.markdown("""
            <div class="header-card">
                <h1>Daily Progress Tracker</h1>
                <p>Track your fitness journey every day!</p>
            </div>
        """, unsafe_allow_html=True)

        current_plan = get_current_plan(username)
        if current_plan:
            with st.expander("View Your Current Plan"):
                st.markdown("""
                    <div class="plan-card">
                        <h3>Your Current Plan</h3>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(current_plan)
        else:
            st.info("No plan generated yet! Go to Generate Plan first.")

        st.markdown("---")

        with st.form("progress_form"):
            col1, col2 = st.columns(2)

            with col1:
                weight = st.number_input("Today's Weight (kg)",
                    min_value=30.0, max_value=200.0, value=70.0)
                water_intake = st.number_input("Water Intake (Litres)",
                    min_value=0.0, max_value=10.0, value=2.0)

            with col2:
                workout_done = st.selectbox("Workout Done?", ["Yes", "No"])
                sleep_hours = st.number_input("Sleep Hours",
                    min_value=0.0, max_value=12.0, value=7.0)

            notes = st.text_area("Notes", placeholder="How was your day?...")
            submitted = st.form_submit_button("Log Progress")

        if submitted:
            message = log_progress(
                username,
                weight, workout_done,
                water_intake, sleep_hours, notes
            )
            st.toast(message, icon="✅")
            st.balloons()

    # ==================
    # PAGE 3 — View History
    # ==================
    elif page == "View History":

        st.markdown("""
            <div class="header-card">
                <h1>Progress History</h1>
                <p>See how far you've come!</p>
            </div>
        """, unsafe_allow_html=True)

        data = get_progress(username)

        if not data:
            st.info("No progress logged yet! Start tracking.")
        else:
            df = pd.DataFrame(data)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Days", len(df))
            with col2:
                st.metric("Workouts Done", len(df[df["workout_done"] == "Yes"]))
            with col3:
                st.metric("Current Weight", f"{df['weight'].iloc[-1]} kg")
            with col4:
                st.metric("Avg Water", f"{df['water_intake'].mean():.1f}L")

            st.markdown("---")
            st.dataframe(df, use_container_width=True)

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Weight Progress")
                st.line_chart(df.set_index("date")["weight"])
            with col2:
                st.subheader("Water Intake")
                st.line_chart(df.set_index("date")["water_intake"])

            st.subheader("Sleep Hours")
            st.line_chart(df.set_index("date")["sleep_hours"])
