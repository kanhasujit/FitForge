from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recommender import generate_recommendation

# ── App setup ─────────────────────────────────────────────
app = FastAPI(
    title="FitForge API",
    description="AI-powered personalized workout plan generator",
    version="1.0.0"
)

# ── Input schema ──────────────────────────────────────────
class UserProfile(BaseModel):
    age               : int
    gender            : str      # 'Male' or 'Female'
    weight            : float    # in kg
    height            : float    # in meters
    bmi               : float
    experience_level  : int      # 1, 2, or 3
    workout_frequency : int      # days per week
    session_duration  : float    # hours per session
    goal              : str      # 'Weight Loss', 'Muscle Gain', 'Flexibility', 'Endurance'
    location          : str      # 'Home (No Equipment)', 'Home (Basic Equipment)', 'Gym'

# ── Routes ────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Welcome to FitForge API 💪"}

@app.get("/health")
def health():
    return {"status": "API is running ✅"}

@app.post("/recommend")
def recommend(user: UserProfile):
    result = generate_recommendation(user.dict())
    return {
        "status"        : "success",
        "workout_type"  : result['workout_type'],
        "calories"      : result['calories'],
        "difficulty"    : result['difficulty'],
        "location"      : result['location'],
        "exercises"     : result['exercises']
    }