import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def load_data(path):
    df = pd.read_csv(path)
    print("✅ Data Loaded")
    return df


def handle_missing_values(df):
    # For now, just drop (dataset is synthetic so mostly clean)
    df = df.dropna()
    print("✅ Missing values handled")
    return df


def encode_categorical(df):
    le = LabelEncoder()

    df['subject'] = le.fit_transform(df['subject'])
    df['topic'] = le.fit_transform(df['topic'])
    df['learning_style'] = le.fit_transform(df['learning_style'])
    df['quiz_performance'] = le.fit_transform(df['quiz_performance'])

    print("✅ Categorical data encoded")
    return df


def normalize_data(df):
    scaler = StandardScaler()

    numerical_cols = ['score', 'time_spent', 'attempts']
    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

    print("✅ Numerical data normalized")
    return df


def preprocess_pipeline(path):
    df = load_data(path)
    df = handle_missing_values(df)
    df = encode_categorical(df)
    df = normalize_data(df)

    print("✅ Preprocessing completed")
    return df


if __name__ == "__main__":
    df = preprocess_pipeline("../data/student_learning_data.csv")
    print(df.head())