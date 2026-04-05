import streamlit as st

st.set_page_config(
    page_title="AI Learning Path Generator", 
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
import pandas as pd
import matplotlib.pyplot as plt
import json
import numpy as np
import copy

# -------------------------------
# 📚 SUBJECT → TOPIC MAPPING
# -------------------------------
SUBJECT_TOPICS = {
    "Python": ["OOP", "Functions", "Loops", "File Handling"],
    "DSA": ["Queue", "Stack", "Arrays", "Linked List"],
    "OS": ["Processes", "Scheduling", "Threads"],
    "DBMS": ["SQL", "Joins", "Normalization"],
    "CN": ["Routing", "OSI Model", "TCP/IP"]
}

NEXT_TOPIC_MAP = {
    "OOP": "Functions",
    "Functions": "Loops",
    "Loops": "File Handling",
    "File Handling": None,

    "Queue": "Stack",
    "Stack": "Arrays",
    "Arrays": "Linked List",
    "Linked List": None,

    "Processes": "Scheduling",
    "Scheduling": "Threads",
    "Threads": None,

    "SQL": "Joins",
    "Joins": "Normalization",
    "Normalization": None,

    "Routing": "OSI Model",
    "OSI Model": "TCP/IP",
    "TCP/IP": None
}

# -------------------------------
#  STUDENT DATA FUNCTIONS
# -------------------------------
STUDENT_FILE = "data/student_learning_data.csv"
MEMORY_FILE = "data/student_memory.csv"
def load_memory():
    try:
        return pd.read_csv(MEMORY_FILE)
    except:
        return pd.DataFrame(columns=["student_id", "topic", "status"])

def save_memory(df):
    df.to_csv(MEMORY_FILE, index=False)

memory_df = load_memory()
def load_students():
    try:
        df = pd.read_csv(STUDENT_FILE)
        # Ensure required columns exist
        for col in ["student_id","subject","topic","score","learning_style"]:
            if col not in df.columns:
                df[col] = None
        return df
    except FileNotFoundError:
        # Create empty DataFrame with columns
        return pd.DataFrame(columns=["student_id","subject","topic","score","learning_style"])

def save_students(df):
    df.to_csv(STUDENT_FILE, index=False)

# Load students properly
students_df = load_students()
students_df["score"] = pd.to_numeric(students_df.get("score", 0), errors="coerce")
# -------------------------------
# 🎯 SMART SUGGESTIONS FUNCTION
# -------------------------------
def get_suggestions(weak_topics):
    suggestions = []

    for topic in weak_topics.index:
        if topic in ["Loops", "Functions"]:
            suggestions.append(f"Practice coding problems on {topic}")
        elif topic in ["Arrays", "Linked List"]:
            suggestions.append(f"Solve DSA problems on {topic} (LeetCode recommended)")
        elif topic in ["SQL", "Joins"]:
            suggestions.append(f"Practice queries for {topic}")
        elif topic in ["Processes", "Threads"]:
            suggestions.append(f"Revise OS concepts: {topic}")
        else:
            suggestions.append(f"Study basics of {topic}")

    return suggestions

# -------------------------------
# 🗺️ MULTI-WEEK ROADMAP GENERATOR
# -------------------------------
def generate_roadmap(level, weak_topics, current_topic):
    roadmap = []

    # fallback if no weak topics
    topics = list(weak_topics.index)
    if not topics:
        topics = [current_topic]

    for week in range(1, 5):

        week_plan = []

        for t in topics:
            if level == "Beginner":
                week_plan.append(f"Revise basics of {t}")
                week_plan.append(f"Practice easy problems on {t}")

            elif level == "Intermediate":
                week_plan.append(f"Solve medium-level problems on {t}")
                week_plan.append(f"Focus on weak areas in {t}")

            else:
                week_plan.append(f"Build mini project using {t}")
                week_plan.append(f"Solve advanced problems on {t}")

        roadmap.append({
            "week": f"Week {week}",
            "tasks": week_plan
        })

    return roadmap

# -------------------------------
# 🎯 PROGRESS TRACKING (Goal % per topic)
# -------------------------------
def calculate_progress(filtered_df, weak_topics):
    progress = {}
    
    if filtered_df.empty or weak_topics.empty:
        for topic in weak_topics.index:
            progress[topic] = 0
        return progress
    
    topic_scores = filtered_df.groupby("topic")["score"].mean()
    
    for topic in weak_topics.index:
        # normalize score to % progress (0-100)
        progress[topic] = int(topic_scores.get(topic, 0))
        
    return progress

st.markdown("""
<style>

/* 🌈 Soft Gradient Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #fdfbfb, #ebedee);
}

/* Optional: softer purple tint */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7ff, #eef2ff);
}

/* Cards */
.card {
    background: #ffffff;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* Headings */
h1, h2, h3 {
    color: #1e293b;

}

/* Text */
h1, h2, h3, p {
    color: #1e293b;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1e293b;
}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2 {
    color: white !important;
}

/* Inputs */
section[data-testid="stSidebar"] input {
    color: black !important;
    background-color: white !important;
}

/* Selectbox */
section[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: black !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: #111827 !important;
    font-weight: bold;
}

[data-testid="stMetricLabel"] {
    color: #374151 !important;
}

/* TAB FONT SIZE FIX */
button[data-baseweb="tab"] {
    font-size: 18px !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #4f46e5, #2563eb);
    color: white;
    border-radius: 10px;
    height: 3em;
    font-weight: bold;
}

.stButton>button:hover {
    opacity: 0.9;
    transform: scale(1.02);
}

/* Progress */
div[data-testid="stProgressBar"] > div {
    background-color: #22c55e !important;
}

</style>
""", unsafe_allow_html=True)

with open("data/quiz_data.json") as f:
    quiz_data = json.load(f)

if "analyze" not in st.session_state:
    st.session_state.analyze = False

#  Initialize globally (FIX)
weak_topics = pd.Series(dtype=float)
strong_topics = pd.Series(dtype=float)

# -------------------------------
# CONFIG
# -------------------------------


API_URL = "http://127.0.0.1:5001"

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.markdown("""
<h2 style='color:white;'>AI Dashboard</h2>
<hr style='border:1px solid gray'>
""", unsafe_allow_html=True)

# -------------------------------
# 👤 LOGIN SYSTEM
# -------------------------------
st.sidebar.subheader("Student Login")

student_id = st.sidebar.text_input("Enter Student ID")

students_df["score"] = pd.to_numeric(students_df["score"], errors="coerce")

if student_id:
    try:
        student_id = int(student_id)
        st.sidebar.success(f"Logged in as Student {student_id}")
    except:
        st.sidebar.error("Enter valid numeric ID")

if student_id:
    student_history = students_df[students_df["student_id"] == student_id]
else:
    student_history = pd.DataFrame()

score = st.sidebar.slider("Score", 0, 100, 50)
time_spent = st.sidebar.slider("Time Spent (mins)", 10, 180, 60)
attempts = st.sidebar.slider("Attempts", 1, 5, 2)

learning_style = st.sidebar.selectbox(
    "Learning Style",
    ["Visual", "Audio-Visual", "Kinesthetic"]
)
subject = st.sidebar.selectbox(
    "Subject",
    list(SUBJECT_TOPICS.keys())
)

topic = st.sidebar.selectbox(
    "Topic",
    ["All Topics"] + SUBJECT_TOPICS[subject]
)

if topic == "All Topics":
    st.info("You are analyzing subject-level performance")


if st.sidebar.button("Analyze Student", key="analyze_btn"):
    st.session_state.analyze = True
    

if st.sidebar.button("Reset", key="reset_btn"):
    st.session_state.analyze = False
    


# -------------------------------
# TITLE
# -------------------------------
st.markdown("""
<h1 style='text-align: center; color: #2563eb;'>
AI Personalized Learning Path Generator
</h1>
<p style='text-align: center; color: gray;'>
Smart AI system for adaptive learning & performance tracking
</p>
""", unsafe_allow_html=True)

# -------------------------------
# 📊 Topic Performance (USE USER DATA ONLY)
# -------------------------------
st.subheader(" Topic Performance")

# ALWAYS DEFINE filtered_df FIRST
if not students_df.empty and student_id:

    if topic == "All Topics":
        filtered_df = students_df[
            (students_df["student_id"] == student_id) &
            (students_df["subject"] == subject)
        ]
    else:
        filtered_df = students_df[
            (students_df["student_id"] == student_id) &
            (students_df["subject"] == subject) &
            (students_df["topic"] == topic)
        ]
    if "score" not in filtered_df.columns:
        filtered_df["score"] = pd.Series(dtype=float)
else:
    filtered_df = pd.DataFrame(columns=students_df.columns)

# SAFE TO USE
if not filtered_df.empty:
    topic_performance = filtered_df.groupby("topic")["score"].mean()
    st.bar_chart(topic_performance.sort_values(ascending=False))
else:
    st.info("No data available yet")

#Progress Over Time

st.subheader("Progress Over Time")

if not student_history.empty:
    progress = student_history.groupby("topic")["score"].mean()
    st.line_chart(progress)

# -------------------------------
#  Strength vs Weakness
# -------------------------------
if not student_history.empty:
    weak = filtered_df[filtered_df["score"] < 40].shape[0]
    strong = filtered_df[filtered_df["score"] >= 70].shape[0]
else:
    weak = 0
    strong = 0

st.subheader(" Strength vs Weakness")
st.write(f"Weak: {weak} | Strong: {strong}")

#Performance Distribution

st.subheader("Performance Distribution")

# -------------------------------
# Performance Distribution Pie Chart
# -------------------------------
labels = ["Weak", "Average", "Strong"]

# Safe counts
weak_count = int(filtered_df[filtered_df["score"] < 40].shape[0]) if not filtered_df.empty else 0
intermediate_count = int(filtered_df[(filtered_df["score"] >= 40) & (filtered_df["score"] < 70)].shape[0]) if not filtered_df.empty else 0
strong_count = int(filtered_df[filtered_df["score"] >= 70].shape[0]) if not filtered_df.empty else 0

values = [weak_count, intermediate_count, strong_count]

# Only plot if sum > 0
if sum(values) > 0:
    fig, ax = plt.subplots(figsize=(3,3))
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct="%1.1f%%", 
                                      startangle=90, textprops={'fontsize':9}, 
                                      colors=['#ef4444', '#fbbf24', '#22c55e'])
    for t in texts:  # Label font size
        t.set_fontsize(10)
    ax.axis('equal')  # Makes pie circular
    plt.tight_layout(pad=0)
    st.pyplot(fig)
else:
    st.info("No performance data available yet.")


# -------------------------------
# ANALYZE
# -------------------------------
if st.session_state.analyze:
    
    data = {
        "age": 20,  # or add input later
        "gender": "Male",
        "education_level": "Bachelor's",
        "learning_style": learning_style,
        "previous_gpa": 7.5,
        "completed_modules": 10,
        "avg_time_per_module": time_spent,
        "engagement_score": score,
        "distraction_events": attempts,
        "quiz_accuracy": score
    }

    # API CALL
    try:
        response = requests.post(f"{API_URL}/get_learning_path", json=data, timeout=5)
    
        if response.status_code == 200:
            result = response.json()
        else:
            result = {}

    except Exception as e:
        st.error(f"API not working: {e}")
        result = {}
    roadmap = generate_roadmap(
        result.get("level", "Intermediate"),
        weak_topics,
        topic
    )
    if not result:
        result = {
            "level": "Intermediate" if score >= 50 else "Beginner",
            "next_topic": NEXT_TOPIC_MAP.get(topic, "N/A"),
            "recommended_action": "Practice more questions",
            "difficulty": "Medium",
            "explanation": "Fallback logic used (API failed)"
        }
    # -------------------------------
    # SAVE STUDENT DATA
    # -------------------------------
    if student_id:
        
        students_df = students_df[
            ~((students_df["student_id"] == student_id) &
              (students_df["subject"] == subject) &
              (students_df["topic"] == (topic if topic != "All Topics" else "General")))
    ]
        
        new_row = {
            "student_id": student_id,
             "subject": subject,
             "topic": topic if topic != "All Topics" else "General",
             "score": score,
             "learning_style": learning_style
        }

        students_df = pd.concat([students_df, pd.DataFrame([new_row])], ignore_index=True)
        save_students(students_df)

    # 🔁 REFRESH FILTERED DATA AFTER SAVE
    if student_id:
        if topic == "All Topics":
            filtered_df = students_df[
                (students_df["student_id"] == student_id) &
                (students_df["subject"] == subject)
            ]
        else:
            filtered_df = students_df[
                (students_df["student_id"] == student_id) &
                (students_df["subject"] == subject) &
                (students_df["topic"] == topic)
            ]
    # -------------------------------
    # 🔍 WEAK TOPIC DETECTION 
    # -------------------------------

    if not filtered_df.empty:
        topic_performance = filtered_df.groupby("topic")["score"].mean()
        weak_topics = topic_performance[topic_performance < 40]
        strong_topics = topic_performance[topic_performance >= 70]
    else:
        weak_topics = pd.Series(dtype=float)
        strong_topics = pd.Series(dtype=float)
    progress_percent = calculate_progress(filtered_df, weak_topics)
    
    #Smart Suggestions

    st.subheader(" Smart Suggestions")

    suggestions = get_suggestions(weak_topics)

    if suggestions:
        for s in suggestions:
            st.info(s)
    else:
        st.success("No weak topics — keep going strong!")
    
    # -------------------------------
    # UPDATE MEMORY (STRONG / WEAK)
    # -------------------------------
    if student_id and not filtered_df.empty:
        topic_perf = filtered_df.groupby("topic")["score"].mean()

        for t, val in topic_perf.items():
            if val < 40:
                status = "Weak"
            elif val >= 70:
                status = "Strong"
            else:
                status = "Neutral"

            # Remove old record
            memory_df = memory_df[
                ~((memory_df["student_id"] == student_id) & (memory_df["topic"] == t))
            ]

            # Add new record
            memory_df = pd.concat([memory_df, pd.DataFrame([{
                "student_id": student_id,
                "topic": t,
                "status": status
            }])], ignore_index=True)

        save_memory(memory_df)
    # -------------------------------
    # 📊 KPI CARDS
    # -------------------------------

    # Safe defaults (avoid errors if not defined)
    weak_topics = weak_topics if 'weak_topics' in locals() else []
    strong_topics = strong_topics if 'strong_topics' in locals() else []

    col1, col2, col3 = st.columns(3)

    # Total Records
    col1.markdown(f"""
    <div class="card">
    <h3>Total Records</h3>
    <h2>{len(students_df)}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Weak Topics
    col2.markdown(f"""
    <div class="card">
    <h3>Weak Topics</h3>
    <h2>{len(weak_topics)}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Strong Topics
    col3.markdown(f"""
    <div class="card">
    <h3>Strong Topics</h3>
    <h2>{len(strong_topics)}</h2>
    </div>
    """, unsafe_allow_html=True)


    st.subheader("Improvement Suggestions")

    for topic in weak_topics.index:
        st.error(f"⚠️ Focus on {topic}")
        st.caption("Revise basics + practice questions")
    
    #SHOW MEMORY IN UI

    st.subheader(" Learning Memory")
    user_memory = memory_df[memory_df["student_id"] == student_id]
    if not user_memory.empty:
        st.dataframe(user_memory)
    else:
        st.info("No memory data yet")

    # -------------------------------
    # 🎯 QUIZ RECOMMENDATION LOGIC
    # -------------------------------
    recommended_quizzes = []

    for weak_topic in weak_topics.index:
        for quiz in quiz_data:
            if quiz["topic"].lower() == weak_topic.lower():
                
                # Dynamic difficulty adjustment
                quiz_copy = copy.deepcopy(quiz)
                if score < 40:
                    quiz_copy["difficulty"] = "Easy"
                    quiz_copy["questions"] = 5
                elif score < 70:
                    quiz_copy["difficulty"] = "Medium"
                    quiz_copy["questions"] = 7
                else:
                    quiz_copy["difficulty"] = "Hard"
                    quiz_copy["questions"] = 10

                recommended_quizzes.append(quiz_copy)
                
    # -------------------------------
    # 🔥 HEATMAP DATA
    # -------------------------------
    heatmap_data = filtered_df.pivot_table(
        index="topic",
        columns="learning_style",
        values="score",
        aggfunc="mean"
    )
    # -------------------------------
    # 🔥 TABS
    # -------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview",
        "Analytics",
        "Learning Plan",
        "Resources"
    ])

    # -------------------------------
    # 📊 TAB 1: OVERVIEW
    # -------------------------------
    with tab1:
        

        st.subheader("Student Overview")

        col1, col2, col3 = st.columns(3)
        col1.metric("Level", result.get("level", "N/A"))
        col2.metric("Score", score)
        col3.metric("Learning Style", learning_style)

        

        st.subheader("Performance Insight")

        if score < 40:
            st.error("Weak in fundamentals")
        elif score < 70:
            st.warning("Needs practice")
        else:
            st.success("Strong performance")

        st.subheader("Progress")
        st.progress(score / 100)

    # -------------------------------
    # 📈 TAB 2: ANALYTICS
    # -------------------------------
    with tab2:
        st.markdown("""
        <h1 style='text-align:center; color:#4f46e5; margin-bottom:20px;'>
        Welcome to Your Analytics Dashboard
        </h1>
        """, unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'> Performance Analytics</h2>", unsafe_allow_html=True)

        # -------------------------------
        # 🏆 TOP PERFORMERS
        # -------------------------------
        st.markdown("<h2 style='text-align:center;'>🏆 Top 5 Performers</h2>", unsafe_allow_html=True)

        if not students_df.empty:
            top_students = students_df.groupby("student_id")["score"].mean().nlargest(5)

            fig, ax = plt.subplots(figsize=(5,3))

            ax.bar(
                top_students.index.astype(str),
                top_students.values,
                color=["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#3b82f6"]
            )

            ax.set_title("Top 5 Students", fontsize=10)
            ax.set_xlabel("Student ID", fontsize=8)
            ax.set_ylabel("Score", fontsize=8)

            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.pyplot(fig)
        else:
            st.info("No student data available")

        #table of all students and their scores
        st.markdown("<h2 style='text-align:center;'>Student Results Record</h2>", unsafe_allow_html=True)

        if not students_df.empty:
            top_topics = students_df.sort_values("score", ascending=False).groupby("student_id").head(3)

            top_topics["score"] = pd.to_numeric(top_topics["score"], errors="coerce")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.dataframe(top_topics)

        # -------------------------------
        # 📚 SUBJECT PERFORMANCE
        # -------------------------------
        st.markdown("<h2 style='text-align:center;'> Subject-wise Performance Analysis</h2>", unsafe_allow_html=True)

        if not students_df.empty:
            students_df["score"] = pd.to_numeric(students_df["score"], errors="coerce")
            subject_avg = students_df.groupby(["student_id", "subject"])["score"].mean().unstack()

            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.bar_chart(subject_avg.fillna(0))
        

            safe_df = subject_avg.fillna(0)

            # Ensure all values are numeric
            safe_df = safe_df.apply(pd.to_numeric, errors="coerce")

            st.dataframe(
                safe_df.style.background_gradient(cmap="Purples")
            )
        else:
            st.info("No subject data available")

        # -------------------------------
        # ⚖️ WEAK vs STRONG DISTRIBUTION
        # -------------------------------
        st.markdown("<h2 style='text-align:center;'> Weak vs Strong Distribution</h2>", unsafe_allow_html=True)

        weak_count = len(weak_topics)
        strong_count = len(strong_topics)

        fig, ax = plt.subplots(figsize=(4,3))

        ax.bar(
            ["Weak", "Strong"],
            [weak_count, strong_count],
            color=["#ef4444", "#22c55e"]
        )

        ax.set_title("Weak vs Strong", fontsize=10)

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.pyplot(fig)


        st.markdown("<h2 style='text-align:center;'> Your Past Records</h2>", unsafe_allow_html=True)

        if not student_history.empty:
            st.dataframe(
                student_history.style
                .background_gradient(cmap="Oranges")
            )
        else:
            st.warning("No records yet")


        # -------------------------------
        # 🔥 HEATMAP (Matplotlib)
        # -------------------------------
        st.subheader(" Performance Heatmap")

        if not heatmap_data.empty:
            fig, ax = plt.subplots()

            cax = ax.imshow(heatmap_data.values)

            ax.set_xticks(range(len(heatmap_data.columns)))
            ax.set_yticks(range(len(heatmap_data.index)))

            ax.set_xticklabels(heatmap_data.columns)
            ax.set_yticklabels(heatmap_data.index)

            plt.colorbar(cax)

            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.pyplot(fig)
        else:
            st.warning("Not enough data for heatmap")


    # -------------------------------
    #  TAB 3: LEARNING PLAN
     # -------------------------------
    with tab3:
        st.subheader(" Personalized Learning Path")

        if not filtered_df.empty:
            weak_topics_list = filtered_df[filtered_df["score"] < 70]["topic"].unique()
            if len(weak_topics_list) > 0:
                next_topic = weak_topics_list[0]  # Pick first weak topic
            else:
                next_topic = "No weak topics, keep practicing!"
        else:
            next_topic = "No data available"

        # Display Next Topic in center
        st.markdown(f"<h3 style='color:#ef4444; 'text-align:center;'>Next Topic: {next_topic}</h3>", unsafe_allow_html=True)
        st.write(f"**Recommended Action:** {result.get('recommended_action', 'N/A')}")
        st.write(f"**Difficulty Level:** {result.get('difficulty', 'N/A')}")

        if "explanation" in result and "Fallback" not in result["explanation"]:
            st.subheader("Why this recommendation?")
            st.info(result["explanation"])

        st.subheader(" Weekly Learning Plan")
        st.subheader("🗺️ 4-Week Personalized Roadmap")

        for week in roadmap:
            st.markdown(f"<h3 style='color:#2563eb'>{week['week']}</h3>", unsafe_allow_html=True)
            for task in week["tasks"]:
                st.markdown(f"<p style='color:#1f2937;'>{task}</p>", unsafe_allow_html=True)

        if "plan" in result:
            for day in result["plan"]:
                st.write(day)
        else:
            st.warning("No weekly plan available")
        
        st.subheader("Topic Progress Tracker")

        if progress_percent:
            for topic, percent in progress_percent.items():
                st.markdown(f"**{topic}:** {percent}% completed")
                st.progress(percent)
        else:
            st.info("No progress data available yet")
      
        st.subheader(" Priority Topics")

        if not weak_topics.empty:
            for topic in weak_topics.index[:3]:
                st.error(f"High Priority: {topic}")
        elif len(filtered_df) < 3:
            st.info("Not enough data to identify weak topics yet")
        else:
            st.success("All topics are strong!")
    # -------------------------------
    # 📚 TAB 4: RESOURCES
    # -------------------------------
    with tab4:
        st.subheader("Smart Recommendations")
        st.info(result.get("resources", "No resources available"))

        st.subheader("🎥 Recommended Video")

        video_links = {
            "Arrays": "https://www.youtube.com/watch?v=QJNwK2uJyGs",
            "Loops": "https://www.youtube.com/watch?v=6iF8Xb7Z3wQ",
            "Scheduling": "https://www.youtube.com/watch?v=2hG7s8oC6Dg",
            "DBMS": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "OS": "https://www.youtube.com/watch?v=26QPDBe-NB8"
        }

        topic_to_watch = next_topic

        if topic_to_watch in video_links:
            st.video(video_links[topic_to_watch])
        else:
            st.markdown(f"[Watch videos on {topic_to_watch}](https://www.youtube.com/results?search_query={topic_to_watch})")

        st.subheader("🏆 Achievements")

        if score > 80:
            st.balloons()
            st.success("🏅 Top Performer ")
        elif score > 50:
            st.info(" Good Progress")
        else:
            st.warning(" Keep Improving")

        if score < 40:
            st.error(" Challenge: Improve your basics this week!")
        
        st.subheader(" Recommended Quizzes")

        if recommended_quizzes:
            for quiz in recommended_quizzes:
                st.markdown(f"""
                **Topic:** {quiz['topic']}  
                Difficulty: {quiz['difficulty']}  
                Questions: {quiz['questions']}  
                [Start Quiz]({quiz['link']})
                """)
        else:
            st.success("No quiz recommendations available yet")