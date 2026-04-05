import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_data(path):
    df = pd.read_csv(path)

    # Score Distribution
    plt.figure()
    sns.histplot(df['score'], bins=20)
    plt.title("Score Distribution")
    plt.savefig("../static/score_distribution.png")

    # Learning Style Count
    plt.figure()
    df['learning_style'].value_counts().plot(kind='bar')
    plt.title("Learning Style Distribution")
    plt.savefig("../static/learning_style.png")

    # Subject vs Score
    plt.figure()
    sns.boxplot(x='subject', y='score', data=df)
    plt.title("Subject vs Score")
    plt.xticks(rotation=45)
    plt.savefig("../static/subject_score.png")

    print("✅ Visualizations saved in /static")


if __name__ == "__main__":
    visualize_data("../data/student_learning_data.csv")