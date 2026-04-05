import pandas as pd
import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

kmeans = joblib.load(os.path.join(BASE_DIR, "models/kmeans.pkl"))
rf_model = joblib.load(os.path.join(BASE_DIR, "models/random_forest.pkl"))
topic_encoder = joblib.load(os.path.join(BASE_DIR, "models/topic_encoder.pkl"))


# -------------------------------
# 1️⃣ RULE-BASED SYSTEM
# -------------------------------
def rule_based_recommendation(score):
    if score < 40:
        return {
            "action": "Revise Basics",
            "difficulty": "Easy"
        }
    elif score < 70:
        return {
            "action": "Practice More",
            "difficulty": "Medium"
        }
    else:
        return {
            "action": "Advance to Next Topic",
            "difficulty": "Hard"
        }


# -------------------------------
# 2️⃣ ML-BASED PREDICTION
# -------------------------------
def predict_next_topic(score, time_spent, attempts):
    import numpy as np

    features = np.array([[score, time_spent, attempts]])
    pred = rf_model.predict(features)

    topic = topic_encoder.inverse_transform(pred)[0]
    return topic


# -------------------------------
# 3️⃣ CLUSTER LEVEL DETECTION
# -------------------------------
def get_student_level(score, time_spent, attempts):
    import numpy as np

    features = np.array([[score, time_spent, attempts]])
    cluster = kmeans.predict(features)[0]

    levels = ["Beginner", "Intermediate", "Advanced"]
    return levels[cluster]


# -------------------------------
# 4️⃣ LEARNING STYLE RESOURCE MAPPING
# -------------------------------
def get_resources(learning_style, topic):
    if learning_style == "Visual":
        return f"Use diagrams and notes for {topic}"
    
    elif learning_style == "Audio-Visual":
        return f"Watch video lectures on {topic}"
    
    elif learning_style == "Kinesthetic":
        return f"Practice coding and quizzes on {topic}"


# -------------------------------
# 5️⃣ FINAL LEARNING PATH GENERATOR
# -------------------------------
def generate_learning_path(student_data):
    score = student_data["score"]
    time_spent = student_data["time_spent"]
    attempts = student_data["attempts"]
    learning_style = student_data["learning_style"]
    
    # Rule-based
    rule = rule_based_recommendation(score)

    # ML prediction
    next_topic = predict_next_topic(score, time_spent, attempts)

    # Level detection
    level = get_student_level(score, time_spent, attempts)

    # Resources
    resources = get_resources(learning_style, next_topic)

    #  NOW use next_topic safely
    plan = generate_week_plan(next_topic)

    # Explanation
    explanation = explain_recommendation(score)

    # Final Output
    learning_path = {
        "level": level,
        "recommended_action": rule["action"],
        "difficulty": rule["difficulty"],
        "next_topic": next_topic,
        "resources": resources,
        "plan": plan,
        "explanation": explanation
    }

    return learning_path

def generate_week_plan(topic):
    return [
        f"Day 1: Learn basics of {topic}",
        f"Day 2: Watch videos on {topic}",
        f"Day 3: Practice problems",
        f"Day 4: Take quiz",
        f"Day 5: Revise mistakes"
    ]

def explain_recommendation(score):
    if score < 40:
        return "Low score → need to strengthen fundamentals"
    elif score < 70:
        return "Moderate score → requires practice"
    else:
        return "High score → ready for advanced topics"

# -------------------------------
# TEST RUN
# -------------------------------
if __name__ == "__main__":
    sample_student = {
        "score": 45,
        "time_spent": 60,
        "attempts": 2,
        "learning_style": "Visual"
    }

    result = generate_learning_path(sample_student)
    print("🎯 Personalized Learning Path:\n")
    print(result)