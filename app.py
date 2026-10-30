
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import secrets
import hmac
import os
import re
import random
import time
from datetime import date

# -------------------- CONFIGURATION --------------------

st.set_page_config(
    page_title="StudyPath",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "studypath.db"
CSV_FILE = "progress.csv"
ITERATIONS = 310_000

# -------------------- DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b0912, #151020, #0b0912);
    color: #f5f3ff;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1450px !important;
    padding: 2rem 2.5rem 3rem 2.5rem !important;
}

[data-testid="stSidebar"] {
    background: #100d19;
    border-right: 1px solid #332343;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #d8c8ff !important;
}

h1 {
    color: #e4d7ff !important;
    font-weight: 750 !important;
    letter-spacing: -0.8px;
}

h2, h3 {
    color: #cbb5ff !important;
    font-weight: 650 !important;
}

p, label, .stMarkdown {
    color: #e8e1f3;
}

[data-testid="stCaptionContainer"] {
    color: #aaa0bd;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #20172d, #171120);
    border: 1px solid #443253;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 5px 18px rgba(0, 0, 0, 0.18);
    transition: border-color 0.2s ease, transform 0.2s ease;
}

div[data-testid="stMetric"]:hover {
    border-color: #9b7be8;
    transform: translateY(-2px);
}

div[data-testid="stMetricLabel"] {
    color: #c0b2d6 !important;
}

div[data-testid="stMetricValue"] {
    color: #f4edff !important;
    font-weight: 750;
}

div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #8052d6, #6335b5);
    color: #ffffff;
    border: 1px solid #9169df;
    border-radius: 10px;
    font-weight: 600;
    min-height: 42px;
    transition: all 0.2s ease;
}

div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(135deg, #9368e8, #7547ca);
    border-color: #c4a7ff;
    color: #ffffff;
}

[data-testid="stSidebar"] div.stButton > button {
    background: linear-gradient(135deg, #39234f, #241832);
    border: 1px solid #624580;
    color: #e9d5ff;
}

[data-testid="stSidebar"] div.stButton > button:hover {
    background: #51316f;
    border-color: #c4a7ff;
}

div[data-testid="stForm"] {
    background: #15101f;
    border: 1px solid #443253;
    border-radius: 16px;
    padding: 22px;
}

input, textarea {
    border-radius: 9px !important;
}

div[data-baseweb="select"] > div {
    border-radius: 9px;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 1px #a78bfa !important;
}

.study-hero {
    background: linear-gradient(120deg, #291846, #1b1428 65%, #171020);
    border: 1px solid #56377c;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 26px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
}

.study-hero h1 {
    margin-bottom: 8px;
    font-size: 2.3rem;
}

.study-muted {
    color: #c0b2d5;
    font-size: 1rem;
    line-height: 1.7;
}

hr {
    border-color: #352641 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #382947;
    border-radius: 12px;
    overflow: hidden;
}

/* Single-line progress bar */
div[data-testid="stProgress"] {
    padding: 0 !important;
    margin: 8px 0 !important;
}

div[data-testid="stProgress"] > div {
    height: 8px !important;
    background: #30223f !important;
    border-radius: 20px !important;
    overflow: hidden;
}

div[data-testid="stProgress"] div[role="progressbar"] {
    height: 8px !important;
    background: #30223f !important;
    border-radius: 20px !important;
    overflow: hidden;
}

div[data-testid="stProgress"] div[role="progressbar"] > div {
    height: 8px !important;
    background: #a78bfa !important;
    border-radius: 20px !important;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 10px 12px;
    border-radius: 10px;
    margin-bottom: 5px;
    transition: background 0.2s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #261a35;
}

[data-testid="stSidebar"] hr {
    border-color: #382846 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    overflow-wrap: anywhere;
}

@media (max-width: 768px) {
    .block-container {
        padding: 1.2rem 1rem 2rem 1rem !important;
    }

    .study-hero {
        padding: 22px;
    }

    .study-hero h1 {
        font-size: 1.8rem;
    }
}
</style>
""", unsafe_allow_html=True)


# -------------------- DATABASE --------------------

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            college TEXT DEFAULT '',
            department TEXT DEFAULT '',
            year TEXT DEFAULT '2nd Year',
            interests TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS learning_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            score REAL NOT NULL,
            total REAL NOT NULL,
            percentage REAL NOT NULL,
            suggestion TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS app_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS study_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Medium',
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
        );
        """)


# -------------------- RECOMMENDATIONS --------------------

def get_suggestion(percentage):
    if percentage >= 80:
        return "Excellent! Keep it up."
    elif percentage >= 50:
        return "Good effort. Practise a few more questions."
    return "Revise basics and practise more."


# -------------------- CSV MIGRATION --------------------

def import_legacy_csv(conn, user_id, account_name):
    already_imported = conn.execute(
        "SELECT value FROM app_meta WHERE key = 'legacy_csv_imported'"
    ).fetchone()

    if already_imported:
        return 0

    if not os.path.exists(CSV_FILE):
        conn.execute(
            "INSERT OR REPLACE INTO app_meta(key, value) VALUES (?, ?)",
            ("legacy_csv_imported", "yes")
        )
        return 0

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception:
        return 0

    df.columns = [str(c).strip().title() for c in df.columns]

    defaults = {
        "Name": account_name,
        "Subject": "General",
        "Topic": "Untitled",
        "Score": 0,
        "Total": 100,
        "Percentage": None,
        "Suggestion": ""
    }

    for column, default in defaults.items():
        if column not in df.columns:
            df[column] = default

    imported = 0

    for _, row in df.iterrows():
        try:
            score = float(row["Score"])
            total = float(row["Total"])

            if total <= 0 or score < 0 or score > total:
                continue

            percentage = round(score / total * 100, 2)

            name = str(row["Name"]).strip()
            subject = str(row["Subject"]).strip()
            topic = str(row["Topic"]).strip()
            suggestion = str(row["Suggestion"]).strip()

            if not name or name.lower() == "nan":
                name = account_name
            if not subject or subject.lower() == "nan":
                subject = "General"
            if not topic or topic.lower() == "nan":
                topic = "Untitled"
            if not suggestion or suggestion.lower() == "nan":
                suggestion = get_suggestion(percentage)

            conn.execute("""
                INSERT INTO learning_records
                (user_id, name, subject, topic, score, total,
                 percentage, suggestion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, name, subject, topic, score, total,
                percentage, suggestion
            ))
            imported += 1

        except (ValueError, TypeError):
            continue

    conn.execute(
        "INSERT OR REPLACE INTO app_meta(key, value) VALUES (?, ?)",
        ("legacy_csv_imported", "yes")
    )

    return imported


# -------------------- PASSWORD SECURITY --------------------

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )

    return salt.hex(), password_hash.hex()


def verify_password(password, salt_hex, stored_hash):
    try:
        salt = bytes.fromhex(salt_hex)
        _, calculated_hash = hash_password(password, salt)
        return hmac.compare_digest(calculated_hash, stored_hash)
    except (ValueError, TypeError):
        return False


# -------------------- ACCOUNT CREATION --------------------

def create_account(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if not name:
        return False, "Enter your name.", None, 0

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Enter a valid email address.", None, 0

    if len(password) < 8:
        return False, "Password must contain at least 8 characters.", None, 0

    salt, password_hash = hash_password(password)
    imported = 0

    try:
        with get_connection() as conn:
            first_user = conn.execute(
                "SELECT COUNT(*) FROM users"
            ).fetchone()[0] == 0

            cursor = conn.execute("""
                INSERT INTO users(name, email, salt, password_hash)
                VALUES (?, ?, ?, ?)
            """, (name, email, salt, password_hash))

            user_id = cursor.lastrowid

            conn.execute(
                "INSERT INTO profiles(user_id) VALUES (?)",
                (user_id,)
            )

            if first_user:
                imported = import_legacy_csv(conn, user_id, name)

        return True, "Account created successfully!", user_id, imported

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists.", None, 0

    except sqlite3.Error:
        return False, "Database error. Your original CSV has not been deleted.", None, 0


def authenticate(email, password):
    with get_connection() as conn:
        user = conn.execute("""
            SELECT id, name, email, salt, password_hash
            FROM users
            WHERE email = ? COLLATE NOCASE
        """, (email.strip(),)).fetchone()

    if user and verify_password(password, user["salt"], user["password_hash"]):
        return dict(user)

    return None


# -------------------- PROFILE --------------------

def get_profile(user_id):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT users.id, users.name, users.email,
                   profiles.college, profiles.department,
                   profiles.year, profiles.interests
            FROM users
            JOIN profiles ON users.id = profiles.user_id
            WHERE users.id = ?
        """, (user_id,)).fetchone()

    return dict(row) if row else None


def update_profile(user_id, name, college, department, year, interests):
    name = name.strip()

    if not name:
        return False

    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET name = ? WHERE id = ?",
            (name, user_id)
        )

        conn.execute("""
            UPDATE profiles
            SET college = ?, department = ?, year = ?, interests = ?
            WHERE user_id = ?
        """, (
            college.strip(), department.strip(), year,
            interests.strip(), user_id
        ))

        conn.execute("""
            UPDATE learning_records SET name = ?
            WHERE user_id = ?
        """, (name, user_id))

    return True


# -------------------- LEARNING RECORDS --------------------

def load_records(user_id):
    with get_connection() as conn:
        df = pd.read_sql_query("""
            SELECT name AS Name,
                   subject AS Subject,
                   topic AS Topic,
                   score AS Score,
                   total AS Total,
                   percentage AS Percentage,
                   suggestion AS Suggestion,
                   created_at AS Date
            FROM learning_records
            WHERE user_id = ?
            ORDER BY id DESC
        """, conn, params=(user_id,))

    return df


def add_record(user_id, name, subject, topic, score, total):
    percentage = round(score / total * 100, 2)
    suggestion = get_suggestion(percentage)

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO learning_records
            (user_id, name, subject, topic, score, total,
             percentage, suggestion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, name, subject, topic, score, total,
            percentage, suggestion
        ))


def delete_user_records(user_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM learning_records WHERE user_id = ?",
            (user_id,)
        )


# -------------------- STUDY PLANNER --------------------

def load_tasks(user_id):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, title, subject, due_date, priority, completed
            FROM study_tasks
            WHERE user_id = ?
            ORDER BY completed ASC, due_date ASC, id DESC
        """, (user_id,)).fetchall()

    return [dict(row) for row in rows]


def add_task(user_id, title, subject, due_date, priority):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO study_tasks
            (user_id, title, subject, due_date, priority)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id, title.strip(), subject.strip(),
            due_date.isoformat(), priority
        ))


def update_task_status(user_id, task_id, completed):
    with get_connection() as conn:
        conn.execute("""
            UPDATE study_tasks
            SET completed = ?
            WHERE id = ? AND user_id = ?
        """, (int(completed), task_id, user_id))


def delete_task(user_id, task_id):
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM study_tasks
            WHERE id = ? AND user_id = ?
        """, (task_id, user_id))


# -------------------- LOGIN / SIGN-UP SCREEN --------------------

def auth_screen():
    st.markdown("""
    <div class="study-hero">
        <h1>📚 StudyPath</h1>
        <h3>Your Student Learning & Progress Assistant</h3>
        <p class="study-muted">
            Track your learning. Understand your progress.
            Build better study habits.
        </p>
    </div>
    """, unsafe_allow_html=True)

    login_tab, signup_tab = st.tabs(["🔐 Login", "✨ Create Account"])

    with login_tab:
        st.subheader("Welcome back!")

        with st.form("login_form"):
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button(
                "Login", use_container_width=True
            )

        if submitted:
            if not email.strip() or not password:
                st.error("Enter both email and password.")
            else:
                user = authenticate(email, password)

                if user:
                    st.session_state.user_id = user["id"]
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")

    with signup_tab:
        st.subheader("Create your student account")

        with st.form("signup_form"):
            name = st.text_input("Full name")
            email = st.text_input("Email address", key="signup_email")
            password = st.text_input(
                "Create password (minimum 8 characters)",
                type="password",
                key="signup_password"
            )
            confirm = st.text_input(
                "Confirm password", type="password"
            )

            submitted = st.form_submit_button(
                "Create Account", use_container_width=True
            )

        if submitted:
            if password != confirm:
                st.error("Passwords do not match.")
            else:
                success, message, user_id, imported = create_account(
                    name, email, password
                )

                if success:
                    st.session_state.user_id = user_id
                    st.session_state.imported_records = imported
                    st.session_state.account_created = True
                    st.rerun()
                else:
                    st.error(message)


# -------------------- START APPLICATION --------------------

init_db()

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    auth_screen()
    st.stop()

profile = get_profile(st.session_state.user_id)

if profile is None:
    st.session_state.user_id = None
    st.rerun()

if st.session_state.get("account_created"):
    imported = st.session_state.pop("imported_records", 0)
    st.session_state.pop("account_created", None)

    st.success("Account created! Welcome to StudyPath.")

    if imported:
        st.info(f"Imported {imported} previous record(s) from progress.csv.")
    elif os.path.exists(CSV_FILE):
        st.info(
            "Your original progress.csv is preserved. "
            "Check Learning History if you expected older records."
        )

# Load the current user's records before displaying the sidebar.
records = load_records(st.session_state.user_id)


# -------------------- PROFESSIONAL SIDEBAR --------------------

with st.sidebar:
    st.markdown("""
    <div style="
        padding: 18px 12px;
        margin-bottom: 18px;
        background: linear-gradient(135deg, #291747, #171020);
        border: 1px solid #55347c;
        border-radius: 16px;
    ">
        <div style="font-size: 30px;">📚</div>
        <div style="
            font-size: 24px;
            font-weight: 800;
            color: #d8b4fe;
        ">StudyPath</div>
        <div style="font-size: 12px; color: #c4b5d9;">
            YOUR PERSONAL LEARNING SPACE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("WORKSPACE")

    page = st.radio(
        "Main navigation",
        [
            "🏠  Dashboard",
            "➕  Add Learning Record",
            "📖  Learning History",
            "🗓️  Study Planner",
            "⏱️  Focus Timer",
            "👤  My Profile"
        ],
        label_visibility="collapsed",
        key="main_navigation"
    )

    page_map = {
        "🏠  Dashboard": "Dashboard",
        "➕  Add Learning Record": "Add Learning Record",
        "📖  Learning History": "Learning History",
        "🗓️  Study Planner": "Study Planner",
        "⏱️  Focus Timer": "Focus Timer",
        "👤  My Profile": "My Profile"
    }

    page = page_map[page]

    st.divider()

    # NEW: Learning Status Card
    total_records = len(records)

    average_score = (
        float(records["Percentage"].mean())
        if not records.empty else 0
    )

    with st.container(border=True):
        st.markdown("### 📊 Learning Status")
        st.metric("📘 Learning Records", total_records)
        st.metric("📈 Average Score", f"{average_score:.1f}%")
        st.progress(
            min(100, max(0, int(average_score))) / 100
        )
        st.caption("Keep learning a little every day!")

    # Signed-in profile
    st.markdown(f"""
    <div style="
        padding: 14px;
        border: 1px solid #3d2b51;
        background: #191323;
        border-radius: 12px;
        margin-top: 14px;
        margin-bottom: 12px;
    ">
        <div style="font-size: 11px; color: #a99abb;">
            SIGNED IN AS
        </div>
        <div style="
            font-size: 16px;
            font-weight: 700;
            color: #f5f3ff;
            margin-top: 5px;
            overflow-wrap: anywhere;
        ">👤 {profile['name']}</div>
        <div style="
            font-size: 11px;
            color: #b9a9ca;
            margin-top: 4px;
            overflow-wrap: anywhere;
        ">{profile['email']}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↪ Sign Out", use_container_width=True):
        st.session_state.user_id = None
        st.rerun()

    st.markdown("""
    <div style="
        text-align: center;
        color: #81718f;
        font-size: 11px;
        margin-top: 24px;
    ">
        STUDYPATH · LEARN EVERY DAY
    </div>
    """, unsafe_allow_html=True)


# -------------------- DASHBOARD --------------------

if page == "Dashboard":
    st.markdown("""
    <div class="study-hero">
        <h1>Welcome to StudyPath 💜</h1>
        <p class="study-muted">
            Your learning journey, organised in one place.
            Small steps lead to big progress.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # NEW: Quick Study Tip button
    study_tips = [
        "Revise one difficult concept before starting a new topic.",
        "Practise coding daily, even if it is only for 20 minutes.",
        "Break a large topic into smaller, manageable tasks.",
        "Explain the logic of a solved problem in your own words.",
        "Review your mistakes instead of repeating only easy questions.",
        "Take short breaks to maintain concentration.",
        "Practise DSA consistently instead of studying everything at once."
    ]

    if "daily_study_tip" not in st.session_state:
        st.session_state.daily_study_tip = study_tips[0]

    with st.container(border=True):
        st.subheader("💡 Quick Study Tip")
        st.write(st.session_state.daily_study_tip)

        if st.button(
            "✨ Get Another Tip",
            key="quick_study_tip",
            use_container_width=True
        ):
            available_tips = [
                tip for tip in study_tips
                if tip != st.session_state.daily_study_tip
            ]
            st.session_state.daily_study_tip = random.choice(
                available_tips
            )
            st.rerun()

    st.subheader("📊 Your Learning Overview")

    total_records = len(records)
    average_score = (
        float(records["Percentage"].mean())
        if total_records else 0
    )
    best_score = (
        float(records["Percentage"].max())
        if total_records else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("📘 Learning Records", total_records)
    col2.metric("📈 Average Score", f"{average_score:.1f}%")
    col3.metric("🏆 Best Score", f"{best_score:.1f}%")

    st.divider()

    if records.empty:
        st.info(
            "No learning records yet. "
            "Open 'Add Learning Record' to begin!"
        )
    else:
        subject_data = (
            records.groupby("Subject", as_index=False)["Percentage"]
            .mean()
            .sort_values("Percentage", ascending=False)
        )

        st.subheader("🎯 Your Performance Insights")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Overall Progress**")
            st.progress(
                int(min(100, max(0, average_score)))
            )
            st.write(
                f"Your average performance is **{average_score:.1f}%**."
            )

        with col2:
            st.write("**Learning Insight**")

            if average_score >= 80:
                st.success(
                    "Excellent progress! Keep practising to maintain it."
                )
            elif average_score >= 60:
                st.info(
                    "Good progress! Regular revision can help you improve."
                )
            else:
                st.warning(
                    "Focus on the basics and practise topics regularly."
                )

        st.divider()
        left, right = st.columns(2)

        with left:
            st.subheader("📚 Subject-wise Performance")
            st.bar_chart(
                subject_data.set_index("Subject")["Percentage"]
            )

            best_subject = subject_data.iloc[0]
            st.write(
                f"🌟 Strongest subject: **{best_subject['Subject']}** "
                f"({best_subject['Percentage']:.1f}%)"
            )

        with right:
            st.subheader("💡 Topics to Practise")

            weak_topics = (
                records.dropna(subset=["Topic"])
                .groupby("Topic", as_index=False)["Percentage"]
                .mean()
                .sort_values("Percentage")
                .head(5)
            )

            if weak_topics.empty:
                st.write("Add topic names to see practice suggestions.")
            else:
                for _, row in weak_topics.iterrows():
                    score = float(row["Percentage"])
                    st.write(f"📌 **{row['Topic']}** — {score:.1f}%")

                    if score < 60:
                        st.caption(
                            "Recommendation: Revise the basics and practise."
                        )
                    elif score < 80:
                        st.caption(
                            "Recommendation: Practise more questions."
                        )
                    else:
                        st.caption(
                            "Recommendation: Revise occasionally."
                        )

        st.divider()
        st.subheader("🕘 Recent Learning Activity")
        st.dataframe(
            records.head(5),
            use_container_width=True,
            hide_index=True
        )


# -------------------- ADD LEARNING RECORD --------------------

elif page == "Add Learning Record":
    st.markdown("# ✨ Add Learning Record")
    st.write("Record your practice and track your progress.")

    subjects = [
        "C Programming", "C++", "Java", "Python",
        "Data Structures", "Mathematics",
        "Artificial Intelligence", "Other"
    ]

    with st.form("record_form"):
        subject = st.selectbox("Subject", subjects)

        topic = st.text_input("Topic or chapter")

        if subject == "Other":
            custom_subject = st.text_input("Enter subject name")
        else:
            custom_subject = subject

        col1, col2 = st.columns(2)

        with col1:
            score = st.number_input(
                "Score obtained", min_value=0.0,
                value=0.0, step=1.0
            )

        with col2:
            total = st.number_input(
                "Total marks", min_value=1.0,
                value=100.0, step=1.0
            )

        submitted = st.form_submit_button(
            "Save Learning Record", use_container_width=True
        )

    if submitted:
        if not topic.strip():
            st.error("Please enter the topic.")
        elif not custom_subject.strip():
            st.error("Please enter a subject.")
        elif score > total:
            st.error("Score cannot be greater than total marks.")
        else:
            add_record(
                st.session_state.user_id,
                profile["name"],
                custom_subject.strip(),
                topic.strip(),
                score,
                total
            )

            percentage = round(score / total * 100, 2)
            st.success("Learning record saved successfully!")
            st.metric("Your Score", f"{percentage:.1f}%")
            st.info(get_suggestion(percentage))


# -------------------- LEARNING HISTORY --------------------

elif page == "Learning History":
    st.markdown("# 📖 Learning History")
    st.write("Search, review and export your learning records.")

    if records.empty:
        st.info("No records available yet.")
    else:
        search = st.text_input(
            "🔍 Search by subject or topic"
        ).strip().lower()

        filtered = records.copy()

        if search:
            mask = (
                filtered["Subject"].astype(str).str.lower().str.contains(
                    search, na=False
                )
                | filtered["Topic"].astype(str).str.lower().str.contains(
                    search, na=False
                )
            )
            filtered = filtered[mask]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download My Records as CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="studypath_learning_history.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.divider()
        st.subheader("⚠️ Clear Learning History")

        confirm_delete = st.checkbox(
            "I understand this permanently deletes my learning records."
        )

        if st.button(
            "Delete My Records",
            disabled=not confirm_delete
        ):
            delete_user_records(st.session_state.user_id)
            st.success("Your learning records have been deleted.")
            st.rerun()


# -------------------- STUDENT PROFILE --------------------

elif page == "My Profile":
    st.markdown("# 👤 My Student Profile")
    st.write("Update your details and learning interests.")

    with st.form("profile_form"):
        name = st.text_input("Full name", value=profile["name"])

        st.text_input(
            "Registered email",
            value=profile["email"],
            disabled=True
        )

        college = st.text_input(
            "College", value=profile["college"] or ""
        )

        department = st.text_input(
            "Department", value=profile["department"] or ""
        )

        years = [
            "1st Year", "2nd Year", "3rd Year", "4th Year", "Other"
        ]

        current_year = profile["year"] or "2nd Year"
        year_index = (
            years.index(current_year)
            if current_year in years else years.index("Other")
        )

        year = st.selectbox("Year of study", years, index=year_index)

        interests = st.text_area(
            "Learning interests and goals",
            value=profile["interests"] or "",
            placeholder="Example: Python, DSA, AI, placements..."
        )

        submitted = st.form_submit_button(
            "Save Profile", use_container_width=True
        )

    if submitted:
        if not name.strip():
            st.error("Name cannot be empty.")
        else:
            update_profile(
                st.session_state.user_id,
                name, college, department, year, interests
            )
            st.success("Profile updated successfully!")
            st.rerun()

    st.divider()
    st.caption(
        "Your account details and learning records are private "
        "to your account within this app."
    )


# -------------------- FOCUS TIMER --------------------

elif page == "Focus Timer":
    st.title("⏱️ Focus Timer")
    st.write("Focus on one task at a time. You can do this!")

    if "focus_seconds" not in st.session_state:
        st.session_state.focus_seconds = 25 * 60

    if "focus_running" not in st.session_state:
        st.session_state.focus_running = False

    if "focus_mode" not in st.session_state:
        st.session_state.focus_mode = "Focus"

    focus_mode = st.radio(
        "Choose your session",
        ["Focus", "Short Break"],
        horizontal=True
    )

    if focus_mode != st.session_state.focus_mode:
        st.session_state.focus_mode = focus_mode
        st.session_state.focus_running = False
        st.session_state.focus_seconds = (
            25 * 60 if focus_mode == "Focus" else 5 * 60
        )

    total_seconds = 25 * 60 if focus_mode == "Focus" else 5 * 60

    if st.session_state.focus_seconds > total_seconds:
        st.session_state.focus_seconds = total_seconds

    minutes = st.session_state.focus_seconds // 60
    seconds = st.session_state.focus_seconds % 60

    st.markdown(
        f"""
        <div style="text-align:center; padding:30px;
                    border-radius:20px;
                    background:linear-gradient(135deg,#21143d,#101827);">
            <h2>{focus_mode} Session</h2>
            <h1 style="font-size:64px; color:#c4b5fd;">
                {minutes:02d}:{seconds:02d}
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("▶ Start / Resume", use_container_width=True):
            st.session_state.focus_running = True
            st.rerun()

    with col2:
        if st.button("⏸ Pause", use_container_width=True):
            st.session_state.focus_running = False
            st.rerun()

    with col3:
        if st.button("↻ Reset", use_container_width=True):
            st.session_state.focus_running = False
            st.session_state.focus_seconds = total_seconds
            st.rerun()

    if st.session_state.focus_running:
        if st.session_state.focus_seconds > 0:
            time.sleep(1)
            st.session_state.focus_seconds -= 1
            st.rerun()
        else:
            st.session_state.focus_running = False
            st.success("Session complete! Take a moment to recharge.")
            st.balloons()

    st.caption("Focus: 25 minutes · Short break: 5 minutes")


# -------------------- STUDY PLANNER --------------------

elif page == "Study Planner":
    st.markdown("""
    <div class="study-hero">
        <h1>🗓️ Study Planner</h1>
        <p class="study-muted">
            Plan your study sessions, organise priorities,
            and complete one task at a time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.user_id
    tasks = load_tasks(user_id)

    completed_count = sum(task["completed"] for task in tasks)
    pending_count = len(tasks) - completed_count

    col1, col2, col3 = st.columns(3)
    col1.metric("📋 Total Tasks", len(tasks))
    col2.metric("⏳ Pending", pending_count)
    col3.metric("✅ Completed", completed_count)

    st.divider()
    st.subheader("➕ Create a Study Task")

    with st.form("study_task_form"):
        title = st.text_input(
            "Task name",
            placeholder="Example: Practise linked lists"
        )

        subject = st.selectbox(
            "Subject",
            [
                "C Programming", "C++", "Java", "Python",
                "Data Structures", "Mathematics",
                "Artificial Intelligence", "Aptitude", "Other"
            ]
        )

        if subject == "Other":
            custom_subject = st.text_input(
                "Enter subject name",
                key="planner_custom_subject"
            )
        else:
            custom_subject = subject

        col1, col2 = st.columns(2)

        with col1:
            due_date = st.date_input(
                "Due date",
                value=date.today(),
                min_value=date.today()
            )

        with col2:
            priority = st.selectbox(
                "Priority", ["High", "Medium", "Low"], index=1
            )

        submitted = st.form_submit_button(
            "➕ Add Task", use_container_width=True
        )

    if submitted:
        if not title.strip():
            st.error("Please enter a task name.")
        elif not custom_subject.strip():
            st.error("Please enter a subject.")
        else:
            add_task(user_id, title, custom_subject, due_date, priority)
            st.success("Study task added!")
            st.rerun()

    st.divider()
    st.subheader("📚 Your Tasks")

    tasks = load_tasks(user_id)

    if not tasks:
        st.info("No tasks yet. Add your first study task above!")
    else:
        show_completed = st.checkbox(
            "Show completed tasks", value=True
        )

        visible_tasks = [
            task for task in tasks
            if show_completed or not task["completed"]
        ]

        for task in visible_tasks:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])

                with col1:
                    st.markdown(f"**{task['title']}**")
                    st.caption(
                        f"{task['subject']} · Due: {task['due_date']} · "
                        f"Priority: {task['priority']}"
                    )

                    if task["completed"]:
                        st.success("Completed")
                    elif task["due_date"] < date.today().isoformat():
                        st.warning("Overdue — reschedule or complete it")

                with col2:
                    done = st.checkbox(
                        "Done",
                        value=bool(task["completed"]),
                        key=f"task_done_{task['id']}"
                    )

                    if done != bool(task["completed"]):
                        update_task_status(user_id, task["id"], done)
                        st.rerun()

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_task_{task['id']}"
                    ):
                        delete_task(user_id, task["id"])
                        st.rerun()

        if tasks and completed_count == len(tasks):
            st.balloons()
            st.success("Amazing! All your study tasks are complete.")
