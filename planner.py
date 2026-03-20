import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

def generate_fitness_plan(age, current_weight, target_weight, height, goal, activity_level, available_time):
    
    # Weight difference calculation
    weight_diff = abs(current_weight - target_weight)
    
    if current_weight > target_weight:
        weight_goal = f"Lose {weight_diff} kg"
    elif current_weight < target_weight:
        weight_goal = f"Gain {weight_diff} kg"
    else:
        weight_goal = "Maintain current weight"

    # BMI calculation
    bmi, bmi_category = calculate_bmi(current_weight, height)

    prompt = f"""
    Create a SHORT fitness plan for:
    - Age: {age}
    - Current Weight: {current_weight} kg
    - Target Weight: {target_weight} kg
    - Weight Goal: {weight_goal}
    - Height: {height} cm
    - Current BMI: {bmi} ({bmi_category})
    - Goal: {goal}
    - Activity: {activity_level}
    - Time: {available_time} mins/day

    Give ONLY:
    1. BMI Status & what it means
    2. Timeline (how many weeks to reach target)
    3. Weekly Workout Plan (bullet points)
    4. Daily Diet Plan (simple)
    5. Daily Water Intake
    6. 3 Key Tips

    Keep it under 300 words!
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an expert fitness coach and nutritionist. 
                Give practical, safe and personalized fitness advice.
                Give SHORT, CRISP and CLEAR fitness plans.
                Use bullet points.
                No long paragraphs.
                Be direct and to the point.
                Always mention BMI status and healthy range.
                Acknowledge user to be in healthy body according to BMI.
                Plan exercise daily.
                Maximum 300 words."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=2000
    )

    return response.choices[0].message.content, bmi, bmi_category


def modify_fitness_plan(current_plan, user_feedback):
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an expert fitness coach.
                User has a fitness plan but wants modifications.
                Give SHORT, CRISP and CLEAR fitness plans.
                Use bullet points.
                No long paragraphs.
                Be direct and to the point.
                Maximum 200 words."""
            },
            {
                "role": "user",
                "content": f"""
                Current Plan:
                {current_plan}
                
                User Feedback:
                {user_feedback}
                
                Modify the plan based on feedback.
                Keep what works, change what user can't do.
                """
            }
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content
