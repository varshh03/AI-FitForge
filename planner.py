import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return round(bmi, 1), category


def call_openrouter(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    #  Working models (fallback list)
    models = [
        "openrouter/free"
    ]

    for model in models:
        try:
            data = {
                "model": model,
                "messages": messages
            }

            response = requests.post(url, headers=headers, json=data)
            result = response.json()

            print(f"Trying model: {model}")
            print("API RESPONSE:", result)

            if "choices" in result:
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"Error with {model}:", e)

    return "⚠️ All AI models failed. Please try again later."

def generate_fitness_plan(age, current_weight, target_weight, height, goal, activity_level, available_time):

    # Weight goal
    weight_diff = abs(current_weight - target_weight)

    if current_weight > target_weight:
        weight_goal = f"Lose {weight_diff} kg"
    elif current_weight < target_weight:
        weight_goal = f"Gain {weight_diff} kg"
    else:
        weight_goal = "Maintain current weight"

    # BMI
    bmi, bmi_category = calculate_bmi(current_weight, height)

    prompt = f"""
    Create a SHORT fitness plan:

    Age: {age}
    Current Weight: {current_weight} kg
    Target Weight: {target_weight} kg
    Goal: {weight_goal}
    Height: {height} cm
    BMI: {bmi} ({bmi_category})
    Fitness Goal: {goal}
    Activity Level: {activity_level}
    Time: {available_time} mins/day

    Give ONLY:
    1. BMI meaning
    2. Timeline
    3. Weekly workout use bullet points
    4. Simple Indian diet
    5. Water intake
    6. 3 tips

    Under 300 words. Use bullet points.
    """

    messages = [
        {
            "role": "system",
            "content": "You are a fitness coach. Give short, clear bullet points."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    plan = call_openrouter(messages)

    return plan, bmi, bmi_category

def modify_fitness_plan(current_plan, user_feedback):

    prompt = f"""
    Modify this fitness plan:

    PLAN:
    {current_plan}

    USER FEEDBACK:
    {user_feedback}

    Keep it short, clear, and practical.
    Use bullet points.
    Max 200 words.
    """

    messages = [
        {
            "role": "system",
            "content": "You are a fitness coach. Modify plans based on user needs."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    return call_openrouter(messages)
