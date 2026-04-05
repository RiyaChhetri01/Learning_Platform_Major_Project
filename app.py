from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)


# -------------------------------
# LOAD MODELS
# -------------------------------

level_model = joblib.load("models/level_model.pkl")
encoders = joblib.load("models/feature_encoders.pkl")

def safe_encode(value, encoder, column_name):
    if value in encoder.classes_:
        return encoder.transform([value])[0]
    else:
        print(f" Unknown {column_name}: {value}")
        return 0
@app.route("/")
def home():
    return "✅ API is running! Use /get_learning_path"
# -------------------------------
# API ROUTE
# -------------------------------
@app.route("/get_learning_path", methods=["POST"])
def get_learning_path():
    data = request.json

    age = data["age"]
    gender = data["gender"]
    education_level = data["education_level"]
    learning_style = data["learning_style"]
    previous_gpa = data["previous_gpa"]
    completed_modules = data["completed_modules"]
    avg_time_per_module = data["avg_time_per_module"]
    engagement_score = data["engagement_score"]
    distraction_events = data["distraction_events"]
    quiz_accuracy = data["quiz_accuracy"]

    
    # -------------------------------
    # LEVEL PREDICTION (NEW MODEL)
    # -------------------------------
    input_data = {
        "age": age,
        "gender": safe_encode(gender, encoders["gender"], "gender"),
        "education_level": safe_encode(education_level, encoders["education_level"], "education_level"),
        "learning_style": safe_encode(learning_style, encoders["learning_style"], "learning_style"),
        "previous_gpa": previous_gpa,
        "completed_modules": completed_modules,
        "avg_time_per_module": avg_time_per_module,
        "engagement_score": engagement_score,
        "distraction_events": distraction_events,
        "quiz_accuracy": quiz_accuracy
    }

    df_input = pd.DataFrame([input_data])

    level = level_model.predict(df_input)[0]


    return jsonify({
        "level": level
        
        
    })

# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)