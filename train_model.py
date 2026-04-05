import pandas as pd
import numpy as np
import joblib
import os
os.makedirs("models", exist_ok=True)
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# -------------------------------
# LOAD DATA
# -------------------------------

# Clean score
df = pd.read_csv("data/AI_Personalized_Learning.csv")

df = df.dropna()

# -------------------------------
# FEATURE SELECTION
# -------------------------------

df = df[[
    "age",
    "gender",
    "education_level",
    "learning_style",
    "previous_gpa",
    "completed_modules",
    "avg_time_per_module",
    "engagement_score",
    "distraction_events",
    "quiz_accuracy"
]]

# -------------------------------
# CREATE LEVEL COLUMN
# -------------------------------
def get_level(acc):
    if acc < 50:
        return "Beginner"
    elif acc < 75:
        return "Intermediate"
    else:
        return "Advanced"

df["level"] = df["quiz_accuracy"].apply(get_level)

categorical_cols = ["gender", "education_level", "learning_style"]

encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# -------------------------------
# FEATURES & TARGET
# -------------------------------
X = df.drop(columns=["level"])
y = df["level"]

# -------------------------------
# TRAIN TEST SPLIT
# -------------------------------


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Train:", len(X_train))
print("Test:", len(X_test))

# -------------------------------
# TRAIN MODEL
# -------------------------------

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)
print(df["education_level"].unique())

# -------------------------------
# EVALUATE MODEL
# -------------------------------
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.2f}")
# -------------------------------
# SAVE MODEL
# -------------------------------


joblib.dump(model, "models/level_model.pkl")
joblib.dump(encoders, "models/feature_encoders.pkl")

print("Model saved successfully!")