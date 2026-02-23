import pickle
import pandas as pd

# ── Load models ──────────────────────────────────────────
with open('../models/calorie_model.pkl', 'rb') as f:
    calorie_model = pickle.load(f)

with open('../models/le_gender.pkl', 'rb') as f:
    le_gender = pickle.load(f)

# ── Load exercise data ────────────────────────────────────
exercise_df = pd.read_csv('../data/exercise_clean.csv')

# ── Mappings ──────────────────────────────────────────────
workout_type_map = {
    'Cardio'  : 'Cardio',
    'Strength': 'Strength',
    'HIIT'    : 'Plyometrics',
    'Yoga'    : 'Stretching'
}

location_equipment_map = {
    'Home (No Equipment)'   : ['Body Only'],
    'Home (Basic Equipment)': ['Body Only', 'Dumbbell', 'Bands', 'Kettlebells'],
    'Gym'                   : ['Body Only', 'Dumbbell', 'Barbell', 'Cable',
                               'Machine', 'Kettlebells', 'Medicine Ball',
                               'Exercise Ball', 'Other']
}

# ── Rule functions ────────────────────────────────────────
def recommend_workout(experience_level, goal, bmi):
    if experience_level == 1:
        if goal == 'Weight Loss':   return 'Cardio'
        elif goal == 'Flexibility': return 'Yoga'
        elif goal == 'Muscle Gain': return 'Strength'
        else:                       return 'Cardio'
    elif experience_level == 2:
        if goal == 'Muscle Gain':                      return 'Strength'
        elif goal == 'Weight Loss' and bmi > 25:       return 'HIIT'
        elif goal == 'Flexibility':                    return 'Yoga'
        else:                                          return 'HIIT'
    else:
        if goal == 'Flexibility': return 'Yoga'
        else:                     return 'HIIT'

def get_difficulty(experience_level):
    if experience_level == 1:   return 'Beginner'
    elif experience_level == 2: return 'Intermediate'
    else:                       return 'Expert'

def get_equipment_list(location):
    return location_equipment_map.get(location, ['Body Only'])

def get_exercises(exercise_type, available_equipment, difficulty):
    filtered = exercise_df[
        (exercise_df['Type'] == exercise_type) &
        (exercise_df['Equipment'].isin(available_equipment)) &
        (exercise_df['Level'] == difficulty)
    ].groupby('BodyPart').head(2).head(10)

    if len(filtered) < 3:
        filtered = exercise_df[
            (exercise_df['Type'] == exercise_type) &
            (exercise_df['Equipment'].isin(available_equipment))
        ].groupby('BodyPart').head(2).head(10)

    return filtered[['Title', 'BodyPart', 'Equipment', 'Level']].to_dict(orient='records')

# ── Main recommendation function ──────────────────────────
def generate_recommendation(user):
    # Workout type
    workout_type = recommend_workout(
        user['experience_level'],
        user['goal'],
        user['bmi']
    )

    # Calories
    gender_encoded = le_gender.transform([user['gender']])[0]
    user_features = [[
        user['age'], gender_encoded, user['weight'],
        user['height'], user['bmi'], user['experience_level'],
        user['workout_frequency'], user['session_duration']
    ]]
    calories = calorie_model.predict(user_features)[0]

    # Difficulty & equipment
    difficulty         = get_difficulty(user['experience_level'])
    available_equipment = get_equipment_list(user['location'])
    exercise_type      = workout_type_map[workout_type]

    # Exercises
    exercises = get_exercises(exercise_type, available_equipment, difficulty)

    return {
        'workout_type' : workout_type,
        'calories'     : round(float(calories), 0),
        'difficulty'   : difficulty,
        'location'     : user['location'],
        'exercises'    : exercises
    }