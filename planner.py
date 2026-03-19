import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_fitness_plan(age, weight, height, goal, activity_level, available_time):
    
    prompt = f"""
    Create a detailed personalized fitness plan for:
    - Age: {age} years
    - Weight: {weight} kg
    - Height: {height} cm
    - Goal: {goal}
    - Activity Level: {activity_level}
    - Available Time: {available_time} minutes per day

    Please provide:
    1. 📋 Weekly Workout Plan (day by day)
    2. 🥗 Daily Diet Plan (breakfast, lunch, dinner, snacks)
    3. 💧 Daily Water Intake
    4. 😴 Sleep Schedule
    5. 💡 Top 5 Tips for achieving the goal

    Make it practical, realistic and motivating!
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an expert fitness coach and nutritionist. Give practical, safe and personalized fitness advice.Give SHORT, CRISP and CLEAR fitness plans.
            Use bullet points and emojis.
            No long paragraphs.
            Be direct and to the point.
            At last what will be the output to tell.
            acknowledge user to be in healthy body acording to BMI.
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

    return response.choices[0].message.content
def modify_fitness_plan(current_plan, user_feedback):
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an expert fitness coach.
                User has a fitness plan but wants modifications.
                Give SHORT and CRISP modified plan.
                Maximum 200 words. Use bullet points."""
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