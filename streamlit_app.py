import streamlit as st
import requests
from fpdf import FPDF
import tempfile
import os
from datetime import date

def add_bg_color():
    st.markdown("""
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1623874514711-0f321325f318?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }

        /* Dark overlay so text is readable */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.65);
            z-index: 0;
        }

        /* Make text white */
        h1, h2, h3, p, label, .stMarkdown {
            color: white !important;
        }

        /* Style input boxes */
        .stTextInput input, .stNumberInput input {
            background-color: rgba(255,255,255,0.1) !important;
            color: white !important;
            border-radius: 8px !important;
        }

        /* Style button */
        .stButton button {
            background: linear-gradient(90deg, #e94560, #0f3460) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-size: 16px !important;
            font-weight: bold !important;
        }

        /* Style metrics */
        .stMetric {
            background-color: rgba(255,255,255,0.15) !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="FitForge 💪",
    page_icon="💪",
    layout="centered"
)
add_bg_color()
# ── Header ────────────────────────────────────────────────
st.title("💪 FitForge")
st.subheader("AI-Powered Personalized Workout Plan Generator")
st.markdown("Fill in your details below and get a workout plan made just for you!")
st.divider()

# ── User Input Form ───────────────────────────────────────
st.header("👤 Your Profile")

col1, col2 = st.columns(2)

with col1:
    name     = st.text_input("Your Name", placeholder="e.g. Rahul")
    age      = st.number_input("Age", min_value=10, max_value=80, value=25)
    gender   = st.selectbox("Gender", ["Male", "Female"])
    weight   = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
    height   = st.number_input("Height (m)", min_value=1.0, max_value=2.5, value=1.75)

with col2:
    goal     = st.selectbox("Your Goal", [
                   "Weight Loss",
                   "Muscle Gain",
                   "Flexibility",
                   "Endurance"
               ])
    experience = st.selectbox("Experience Level", [
                   "Beginner (just starting out)",
                   "Intermediate (some experience)",
                   "Expert (very experienced)"
               ])
    frequency  = st.slider("Workout Days Per Week", 1, 7, 3)
    duration   = st.slider("Session Duration (hours)", 0.5, 3.0, 1.0, step=0.5)
    location   = st.selectbox("Where Will You Workout?", [
                   "Home (No Equipment)",
                   "Home (Basic Equipment)",
                   "Gym"
               ])

# ── Calculate BMI ─────────────────────────────────────────
bmi = round(weight / (height ** 2), 1)
st.info(f"📊 Your BMI: **{bmi}**")

# ── Experience level mapping ──────────────────────────────
experience_map = {
    "Beginner (just starting out)"  : 1,
    "Intermediate (some experience)": 2,
    "Expert (very experienced)"     : 3
}

st.divider()

# ── Generate Plan Button ──────────────────────────────────
if st.button("🚀 Generate My Workout Plan", use_container_width=True):

    with st.spinner("Creating your personalized plan..."):

        # Call FastAPI
        payload = {
            "age"              : int(age),
            "gender"           : gender,
            "weight"           : float(weight),
            "height"           : float(height),
            "bmi"              : float(bmi),
            "experience_level" : experience_map[experience],
            "workout_frequency": int(frequency),
            "session_duration" : float(duration),
            "goal"             : goal,
            "location"         : location
        }

        try:
            response = requests.post(
                "https://fitforge-3.onrender.com/recommend",
                json=payload
            )
            data = response.json()

            if data['status'] == 'success':

                st.success("✅ Your workout plan is ready!")
                st.divider()

                # ── Results ───────────────────────────────
                st.header("🏋️ Your Personalized Plan")

                col3, col4, col5 = st.columns(3)
                col3.metric("Workout Type", data['workout_type'])
                col4.metric("Calories Burned", f"{int(data['calories'])} kcal")
                col5.metric("Difficulty", data['difficulty'])

                st.markdown(f"📍 **Location:** {data['location']}")
                st.divider()

                # ── Health Advisory ───────────────────────
                st.header("🏥 Health Advisory")

                advisory_map = {
                    "Cardio"  : "🫀 Great for heart health and fat burning. Stay hydrated and warm up before starting!",
                    "Strength": "💪 Builds muscle and boosts metabolism. Focus on proper form to avoid injury!",
                    "HIIT"    : "🔥 High intensity — burns maximum calories in less time. Rest well between sessions!",
                    "Yoga"    : "🧘 Improves flexibility and mental focus. Breathe deeply and don't rush the poses!"
                }
                st.info(advisory_map.get(data['workout_type'], "Stay consistent and listen to your body!"))

                st.divider()

                # ── Exercise Table ────────────────────────
                st.header("📋 Your Exercises")

                exercises = data['exercises']
                if exercises:
                    for i, ex in enumerate(exercises, 1):
                        with st.expander(f"Exercise {i} — {ex['Title']}"):
                            st.markdown(f"**Body Part:** {ex['BodyPart']}")
                            st.markdown(f"**Equipment:** {ex['Equipment']}")
                            st.markdown(f"**Level:** {ex['Level']}")
                else:
                    st.warning("No exercises found. Try a different location or goal.")

                st.divider()

                # ── Weekly Plan ───────────────────────────
                st.header("📅 Your Weekly Schedule")

                days = ["Monday", "Tuesday", "Wednesday",
                        "Thursday", "Friday", "Saturday", "Sunday"]

                workout_days = days[:frequency]
                rest_days    = days[frequency:]

                for day in workout_days:
                    st.success(f"✅ {day} — {data['workout_type']} Workout")
                for day in rest_days:
                    st.error(f"😴 {day} — Rest Day")

                st.divider()

                # ── PDF Download ──────────────────────────
                st.header("📥 Download Your Plan")

                def generate_pdf(name, data, bmi, goal, frequency):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_margins(15, 10, 15)
                    pdf.set_auto_page_break(auto=False)

                    # ── Header ────────────────────────────────────────────
                    pdf.set_font("Helvetica", "B", 24)
                    pdf.cell(0, 15, "FitForge Workout Plan", ln=True, align="C")
                    pdf.set_font("Helvetica", "", 12)
                    pdf.cell(0, 8, f"Generated on {date.today().strftime('%B %d, %Y')}", ln=True, align="C")
                    pdf.ln(5)

                    # ── User Profile ──────────────────────────────────────
                    pdf.set_font("Helvetica", "B", 14)
                    pdf.cell(0, 10, "Your Profile", ln=True)
                    pdf.set_font("Helvetica", "", 11)
                    pdf.cell(0, 6, f"Name           : {name}", ln=True)
                    pdf.cell(0, 6, f"Goal           : {goal}", ln=True)
                    pdf.cell(0, 6, f"BMI            : {bmi}", ln=True)
                    pdf.cell(0, 6, f"Workout Days   : {frequency} days/week", ln=True)
                    pdf.cell(0, 6, f"Location       : {data['location']}", ln=True)
                    pdf.ln(5)

                    # ── Plan Summary ──────────────────────────────────────
                    pdf.set_font("Helvetica", "B", 14)
                    pdf.cell(0, 10, "Your Plan", ln=True)
                    pdf.set_font("Helvetica", "", 11)
                    pdf.cell(0, 6, f"Workout Type    : {data['workout_type']}", ln=True)
                    pdf.cell(0, 6, f"Difficulty      : {data['difficulty']}", ln=True)
                    pdf.cell(0, 6, f"Calories/Session: {int(data['calories'])} kcal", ln=True)
                    pdf.ln(5)

                    # ── Exercises ─────────────────────────────────────────
                    pdf.set_font("Helvetica", "B", 14)
                    pdf.cell(0, 10, "Your Exercises", ln=True)
                    pdf.set_font("Helvetica", "", 11)
                    for i, ex in enumerate(data['exercises'], 1):
                        pdf.cell(0, 6, f"{i}. {ex['Title']} ({ex['BodyPart']}) - {ex['Level']}", ln=True)
                    pdf.ln(5)

                    # ── Weekly Schedule ───────────────────────────────────
                    pdf.set_font("Helvetica", "B", 14)
                    pdf.cell(0, 10, "Weekly Schedule", ln=True)
                    pdf.set_font("Helvetica", "", 11)
                    days_all = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
                    for i, day in enumerate(days_all):
                        if i < frequency:
                            pdf.cell(0, 6, f"{day}: {data['workout_type']} Workout", ln=True)
                        else:
                            pdf.cell(0, 6, f"{day}: Rest Day", ln=True)

                    # ── Footer always at bottom of page 1 ────────────────
                    pdf.set_y(-15)
                    pdf.set_font("Helvetica", "I", 9)
                    pdf.cell(0, 8, "Generated by FitForge - Stay consistent, stay strong!", ln=True, align="C")

                    # ── Save ──────────────────────────────────────────────
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    pdf.output(tmp.name)
                    return tmp.name

                # def generate_pdf(name, data, bmi, goal, frequency):
                #     pdf = FPDF()
                #     pdf.add_page()

                #     # Header
                #     pdf.set_font("Helvetica", "B", 24)
                #     pdf.cell(0, 15, "FitForge Workout Plan", ln=True, align="C")
                #     pdf.set_font("Helvetica", "", 12)
                #     pdf.cell(0, 8, f"Generated on {date.today().strftime('%B %d, %Y')}", ln=True, align="C")
                #     pdf.ln(5)

                #     # User info
                #     pdf.set_font("Helvetica", "B", 14)
                #     pdf.cell(0, 10, "Your Profile", ln=True)
                #     pdf.set_font("Helvetica", "", 12)
                #     pdf.cell(0, 8, f"Name           : {name}", ln=True)
                #     pdf.cell(0, 8, f"Goal           : {goal}", ln=True)
                #     pdf.cell(0, 8, f"BMI            : {bmi}", ln=True)
                #     pdf.cell(0, 8, f"Workout Days   : {frequency} days/week", ln=True)
                #     pdf.cell(0, 8, f"Location       : {data['location']}", ln=True)
                #     pdf.ln(5)

                #     # Plan summary
                #     pdf.set_font("Helvetica", "B", 14)
                #     pdf.cell(0, 10, "Your Plan", ln=True)
                #     pdf.set_font("Helvetica", "", 12)
                #     pdf.cell(0, 8, f"Workout Type   : {data['workout_type']}", ln=True)
                #     pdf.cell(0, 8, f"Difficulty     : {data['difficulty']}", ln=True)
                #     pdf.cell(0, 8, f"Calories/Session: {int(data['calories'])} kcal", ln=True)
                #     pdf.ln(5)

                #     # Exercises
                #     pdf.set_font("Helvetica", "B", 14)
                #     pdf.cell(0, 10, "Your Exercises", ln=True)
                #     pdf.set_font("Helvetica", "", 12)
                #     for i, ex in enumerate(data['exercises'], 1):
                #         pdf.cell(0, 8, f"{i}. {ex['Title']} ({ex['BodyPart']}) - {ex['Level']}", ln=True)
                #     pdf.ln(5)

                #     # Weekly schedule
                #     pdf.set_font("Helvetica", "B", 14)
                #     pdf.cell(0, 10, "Weekly Schedule", ln=True)
                #     pdf.set_font("Helvetica", "", 12)
                #     days_all = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
                #     for i, day in enumerate(days_all):
                #         if i < frequency:
                #             pdf.cell(0, 8, f"{day}: {data['workout_type']} Workout", ln=True)
                #         else:
                #             pdf.cell(0, 8, f"{day}: Rest Day", ln=True)

                #     pdf.set_y(-25)
                #     pdf.set_font("Helvetica", "I", 10)
                #     pdf.cell(0, 8, "Generated by FitForge - Stay consistent, stay strong!", ln=True, align="C")
                #     # Save to temp file
                #     tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                #     pdf.output(tmp.name)
                #     return tmp.name

                pdf_path = generate_pdf(name, data, bmi, goal, frequency)

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Download My Workout Plan (PDF)",
                        data=f,
                        file_name=f"FitForge_Plan_{name}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

        except Exception as e:
            st.error(f"❌ Could not connect to API. Make sure FastAPI is running! Error: {e}")