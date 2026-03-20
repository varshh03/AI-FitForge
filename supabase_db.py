import os
from supabase import create_client
from dotenv import load_dotenv
import bcrypt
from datetime import date

load_dotenv()

# Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ==================
# AUTH FUNCTIONS
# ==================

def register_user(username, name, password):
    try:
        # Already exists check pannudu
        existing = supabase.table("profiles")\
            .select("username")\
            .eq("username", username)\
            .execute()

        if existing.data:
            return False, "Username already exists!"

        # Password hash pannudu
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # User create pannudu
        supabase.table("profiles").insert({
            "username": username,
            "name": name,
            "password": hashed_password
        }).execute()

        return True, "Registration successful!"

    except Exception as e:
        return False, str(e)

def login_user(username, password):
    try:
        result = supabase.table("profiles")\
            .select("*")\
            .eq("username", username)\
            .execute()

        if not result.data:
            return False, "Username not found!", None

        user = result.data[0]

        # Password check pannudu
        if bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"].encode("utf-8")
        ):
            return True, "Login successful!", user
        else:
            return False, "Wrong password!", None

    except Exception as e:
        return False, str(e), None

# ==================
# PROFILE FUNCTIONS
# ==================

def save_profile(username, age, current_weight, target_weight, height, goal, activity_level, available_time):
    try:
        supabase.table("profiles").update({
            "age": age,
            "current_weight": current_weight,
            "target_weight": target_weight,
            "height": height,
            "goal": goal,
            "activity_level": activity_level,
            "available_time": available_time
        }).eq("username", username).execute()
        return True
    except Exception as e:
        return False

def get_profile(username):
    try:
        result = supabase.table("profiles")\
            .select("*")\
            .eq("username", username)\
            .execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        return None

# ==================
# PROGRESS FUNCTIONS
# ==================

def save_plan(username, plan):
    try:
        today = str(date.today())
        existing = supabase.table("progress")\
            .select("*")\
            .eq("username", username)\
            .eq("date", today)\
            .execute()

        if existing.data:
            supabase.table("progress").update({
                "current_plan": plan
            }).eq("username", username).eq("date", today).execute()
        else:
            supabase.table("progress").insert({
                "username": username,
                "date": today,
                "current_plan": plan
            }).execute()
        return True
    except Exception as e:
        return False

def log_progress(username, weight, workout_done, water_intake, sleep_hours, notes):
    try:
        today = str(date.today())
        existing = supabase.table("progress")\
            .select("*")\
            .eq("username", username)\
            .eq("date", today)\
            .execute()

        if existing.data:
            supabase.table("progress").update({
                "weight": weight,
                "workout_done": workout_done,
                "water_intake": water_intake,
                "sleep_hours": sleep_hours,
                "notes": notes
            }).eq("username", username).eq("date", today).execute()
            return "Today's progress updated!"
        else:
            supabase.table("progress").insert({
                "username": username,
                "date": today,
                "weight": weight,
                "workout_done": workout_done,
                "water_intake": water_intake,
                "sleep_hours": sleep_hours,
                "notes": notes
            }).execute()
            return "Progress logged successfully!"
    except Exception as e:
        return str(e)

def get_progress(username):
    try:
        result = supabase.table("progress")\
            .select("*")\
            .eq("username", username)\
            .order("date")\
            .execute()
        return result.data
    except Exception as e:
        return []

def get_current_plan(username):
    try:
        result = supabase.table("progress")\
            .select("current_plan")\
            .eq("username", username)\
            .order("date", desc=True)\
            .limit(1)\
            .execute()

        if result.data and result.data[0]["current_plan"]:
            return result.data[0]["current_plan"]
        return None
    except Exception as e:
        return None