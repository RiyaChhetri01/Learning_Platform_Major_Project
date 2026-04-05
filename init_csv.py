import pandas as pd

# Create empty student data CSV with required columns
df = pd.DataFrame(columns=["student_id","subject","topic","score","learning_style"])
df.to_csv("data/student_learning_data.csv", index=False)

print("CSV created successfully ✅")