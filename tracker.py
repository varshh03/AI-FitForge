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
            "notes"
        ])
        df.to_csv(TRACKER_FILE, index=False)

def log_progress(username, weight, workout_done, water_intake, sleep_hours, notes):
    initialize_tracker()
    
    today = str(date.today())
    df = pd.read_csv(TRACKER_FILE)

    # Same user same day check pannudu
    exists = ((df["username"] == username) & (df["date"] == today))

    if exists.any():
        # Update pannudu
        df.loc[exists, "weight"] = weight
        df.loc[exists, "workout_done"] = workout_done
        df.loc[exists, "water_intake"] = water_intake
        df.loc[exists, "sleep_hours"] = sleep_hours
        df.loc[exists, "notes"] = notes
        df.to_csv(TRACKER_FILE, index=False)
        return "Today's progress updated!"
    else:
        # New entry add pannudu
        new_entry = {
            "username": username,
            "date": today,
            "weight": weight,
            "workout_done": workout_done,
            "water_intake": water_intake,
            "sleep_hours": sleep_hours,
            "notes": notes
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(TRACKER_FILE, index=False)
        return "Progress logged successfully!"

def get_progress(username):
    initialize_tracker()
    df = pd.read_csv(TRACKER_FILE)
    # Only this user data return pannudu
    return df[df["username"] == username]