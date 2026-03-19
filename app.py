import streamlit as st
from planner import generate_fitness_plan
from tracker import log_progress, get_progress

st.set_page_config(
    page_title="FitAI",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        width: 100%;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff6b6b;
        transform: scale(1.02);
    }
    .plan-card {
        background-color: #1e2130;
        padding: 25px;
        border-radius: 15px;
        border-top: 3px solid #ff4b4b;
        color: white;
        margin: 15px 0;
    }
    .header-card {
        background: linear-gradient(135deg, #ff4b4b, #ff8c00);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==================
# Sidebar
# ==================
st.sidebar.markdown("""
    <div style="
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #ff4b4b, #ff8c00);
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    ">
        <h2>FitAI</h2>
        <p>Your Personal AI Fitness Coach</p>
    </div>
""", unsafe_allow_html=True)

# Username login
st.sidebar.markdown("---")
username = st.sidebar.text_input("Enter your name to login")

if not username:
    st.warning("Please enter your name in the sidebar to continue!")
    st.stop()

st.sidebar.success(f"Welcome, {username}!")
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
            <h1>AI FitForge</h1>
            <p>Get your personalized workout and diet plan in seconds!</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("fitness_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Personal Details")
            age = st.number_input("Age", min_value=10, max_value=80, value=25)
            weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)

        with col2:
            st.subheader("Fitness Goals")
            goal = st.selectbox("Your Goal", [
                "Weight Loss",
                "Muscle Gain",
                "Stay Fit",
                "Increase Stamina"
            ])
            activity_level = st.selectbox("Activity Level", [
                "Sedentary (No exercise)",
                "Lightly Active (1-2 days/week)",
                "Moderately Active (3-4 days/week)",
                "Very Active (5+ days/week)"
            ])
            available_time = st.slider(
                "Available Time (minutes/day)",
                min_value=15,
                max_value=120,
                value=45
            )

        submitted = st.form_submit_button("Generate My Plan")

    if submitted:
        with st.spinner("AI generating your personalized plan..."):
            plan = generate_fitness_plan(
                age, weight, height,
                goal, activity_level, available_time
            )
            st.session_state.plan = plan
        st.toast("Plan generated successfully!", icon="✅")

    if "plan" in st.session_state:
        st.markdown("---")
        st.markdown(f"""
            <div class="plan-card">
                <h3>Your Personalized Fitness Plan</h3>
                {st.session_state.plan}
            </div>
        """, unsafe_allow_html=True)

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

    with st.form("progress_form"):
        col1, col2 = st.columns(2)

        with col1:
            weight = st.number_input("Today's Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
            water_intake = st.number_input("Water Intake (Litres)", min_value=0.0, max_value=10.0, value=2.0)

        with col2:
            workout_done = st.selectbox("Workout Done?", ["Yes", "No"])
            sleep_hours = st.number_input("Sleep Hours", min_value=0.0, max_value=12.0, value=7.0)

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
    st.markdown("---")
    st.subheader("Not comfortable with something?")
    
    feedback = st.text_input(
        "Tell AI what to change",
        placeholder="Ex: I can't do running, I have knee pain..."
    )
    
    if st.button("Modify My Plan"):
        if feedback:
            with st.spinner("AI modifying your plan..."):
                from planner import modify_fitness_plan
                modified = modify_fitness_plan(
                    st.session_state.plan,
                    feedback
                )
                st.session_state.plan = modified
            st.toast("Plan modified!", icon="✅")
            st.rerun()
        else:
            st.warning("Please enter your feedback!")

    df = get_progress(username)

    if df.empty:
        st.info("No progress logged yet! Start tracking.")
    else:
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
