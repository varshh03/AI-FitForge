import pandas as pd
import os
from datetime import date

TRACKER_FILE = "progress.csv"

def initialize_tracker():
    if not os.path.exists(TRACKER_FILE):
        df = pd.DataFrame(columns=[
            "username",
            "date",
            "weight",
            "workout_done",
            "water_intake",
            "sleep_hours",
            "current_plan",
            "notes"
        ])
        df.to_csv(TRACKER_FILE, index=False)
    else:
        df = pd.read_csv(TRACKER_FILE)
        if "current_plan" not in df.columns:
            df["current_plan"] = ""
            df.to_csv(TRACKER_FILE, index=False)

def save_plan(username, plan):
    initialize_tracker()
    today = str(date.today())
    df = pd.read_csv(TRACKER_FILE)

    exists = ((df["username"] == username) & (df["date"] == today))

    if exists.any():
        df.loc[exists, "current_plan"] = plan
    else:
        new_entry = {
            "username": username,
            "date": today,
            "weight": "",
            "workout_done": "",
            "water_intake": "",
            "sleep_hours": "",
            "current_plan": plan,
            "notes": ""
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

    df.to_csv(TRACKER_FILE, index=False)

def log_progress(username, weight, workout_done, water_intake, sleep_hours, notes):
    initialize_tracker()
    today = str(date.today())
    df = pd.read_csv(TRACKER_FILE)

    exists = ((df["username"] == username) & (df["date"] == today))

    if exists.any():
        df.loc[exists, "weight"] = weight
        df.loc[exists, "workout_done"] = workout_done
        df.loc[exists, "water_intake"] = water_intake
        df.loc[exists, "sleep_hours"] = sleep_hours
        df.loc[exists, "notes"] = notes
        df.to_csv(TRACKER_FILE, index=False)
        return "Today's progress updated!"
    else:
        new_entry = {
            "username": username,
            "date": today,
            "weight": weight,
            "workout_done": workout_done,
            "water_intake": water_intake,
            "sleep_hours": sleep_hours,
            "current_plan": "",
            "notes": notes
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(TRACKER_FILE, index=False)
        return "Progress logged successfully!"

def get_progress(username):
    initialize_tracker()
    df = pd.read_csv(TRACKER_FILE)
    return df[df["username"] == username]

def get_current_plan(username):
    initialize_tracker()
    df = pd.read_csv(TRACKER_FILE)
    user_df = df[df["username"] == username]

    if user_df.empty:
        return None

    plans = user_df[user_df["current_plan"] != ""]
    if plans.empty:
        return None

    return plans.iloc[-1]["current_plan"]
