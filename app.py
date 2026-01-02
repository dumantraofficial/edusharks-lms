import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import time
from datetime import datetime

# ==========================================
# 1. APP CONFIGURATION & SETUP
# ==========================================
st.set_page_config(
    page_title="Edu Sharks Pro",
    layout="wide",
    page_icon="🦈",
    initial_sidebar_state="collapsed"
)

# --- DATABASE CONNECTION ---
CONN = sqlite3.connect('edusharks_master.db', check_same_thread=False)
C = CONN.cursor()

# --- INITIALIZE DATABASE TABLES ---
def init_db():
    # 1. Users Table
    C.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, mobile TEXT, name TEXT, joined_at TEXT)''')
    
    # 2. Courses Table
    C.execute('''CREATE TABLE IF NOT EXISTS courses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, stream TEXT, subject TEXT, 
                  title TEXT, link TEXT, type TEXT, uploaded_by TEXT, date TEXT)''')
    
    # 3. Progress/Activity Table
    C.execute('''CREATE TABLE IF NOT EXISTS activity 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, action TEXT, details TEXT, timestamp TEXT)''')

    # Create Default Admin if not exists
    try:
        # Pass: admin123
        admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
        C.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                  ('admin', admin_hash, 'admin', '0000000000', 'Super Admin', str(datetime.now())))
        CONN.commit()
    except sqlite3.IntegrityError:
        pass

init_db()

# ==========================================
# 2. HELPER FUNCTIONS (BACKEND LOGIC)
# ==========================================
def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_user(username, password):
    pwd_hash = make_hash(password)
    C.execute("SELECT role, name FROM users WHERE username=? AND password=?", (username, pwd_hash))
    return C.fetchone()

def create_user(username, password, mobile, name):
    try:
        C.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                  (username, make_hash(password), 'student', mobile, name, str(datetime.now())))
        CONN.commit()
        return True
    except:
        return False

def log_activity(username, action, details):
    C.execute("INSERT INTO activity (username, action, details, timestamp) VALUES (?, ?, ?, ?)",
              (username, action, details, str(datetime.now())))
    CONN.commit()

def get_courses(cat=None, stream=None, sub=None):
    query = "SELECT title, link, type, date FROM courses"
    conditions = []
    params = []
    
    if cat:
        conditions.append("category=?")
        params.append(cat)
    if stream:
        conditions.append("stream=?")
        params.append(stream)
    if sub:
        conditions.append("subject=?")
        params.append(sub)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    C.execute(query, tuple(params))
    return C.fetchall()

# ==========================================
# 3. CUSTOM CSS (PREMIUM UI)
# ==========================================
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #f0f2f5; }
    
    /* Login Container */
    .login-box {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Metrics Cards */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #5A4FCF;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Custom Buttons */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: 0.3s;
    }
    
    /* Card Style for Content */
    .content-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #e1e4e8;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e1e2f;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SESSION STATE MANAGEMENT
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = {} # Stores username, name, role

# ==========================================
# 5. UI VIEWS (SCREENS)
# ==========================================

# --- A. AUTH SCREEN (LOGIN/SIGNUP) ---
def auth_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    
    with c2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=80)
        st.markdown("<h2>Edu Sharks LMS</h2>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            l_user = st.text_input("Username")
            l_pass = st.text_input("Password", type="password")
            if st.button("Access Portal", use_container_width=True):
                user = check_user(l_user, l_pass)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_info = {'username': l_user, 'role': user[0], 'name': user[1]}
                    log_activity(l_user, "Login", "User logged in successfully")
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

        with tab2:
            r_user = st.text_input("New Username")
            r_pass = st.text_input("New Password", type="password")
            r_name = st.text_input("Full Name")
            r_mob = st.text_input("Mobile Number")
            
            if st.button("Create Student ID", use_container_width=True):
                if r_user and r_pass:
                    if create_user(r_user, r_pass, r_mob, r_name):
                        st.success("Account Created! Login now.")
                    else:
                        st.error("Username already taken!")
                else:
                    st.warning("Fill all details")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- B. STUDENT DASHBOARD ---
def student_dashboard():
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.title(st.session_state.user_info['name'])
        st.caption("Student Dashboard")
        menu = st.radio("Menu", ["📊 Dashboard", "📚 My Classroom", "👤 Profile"])
        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "📊 Dashboard":
        st.title("👋 Welcome Back!")
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Courses Enrolled", "4")
        m2.metric("Pending Assignments", "2", "-1")
        m3.metric("Attendance", "87%", "+2%")
        
        # Analytics Chart (Dummy Data)
        st.subheader("Weekly Progress")
        chart_data = pd.DataFrame({'Hours': [2, 4, 1, 5, 3, 6, 4]}, index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        st.bar_chart(chart_data)

    elif menu == "📚 My Classroom":
        st.title("🎓 Digital Classroom")
        
        # Smart Filters
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        
        # Get Categories dynamically from DB
        C.execute("SELECT DISTINCT category FROM courses")
        cats = [row[0] for row in C.fetchall()]
        sel_cat = c1.selectbox("Category", ["All"] + cats)
        
        # Get Streams based on Cat
        streams = []
        if sel_cat != "All":
            C.execute("SELECT DISTINCT stream FROM courses WHERE category=?", (sel_cat,))
            streams = [row[0] for row in C.fetchall()]
        sel_stream = c2.selectbox("Stream", ["All"] + streams)
        
        # Get Subjects
        subs = []
        if sel_stream != "All":
            C.execute("SELECT DISTINCT subject FROM courses WHERE stream=?", (sel_stream,))
            subs = [row[0] for row in C.fetchall()]
        sel_sub = c3.selectbox("Subject", ["All"] + subs)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show Content
        content = get_courses(
            None if sel_cat=="All" else sel_cat,
            None if sel_stream=="All" else sel_stream,
            None if sel_sub=="All" else sel_sub
        )
        
        if content:
            for item in content:
                # item = (title, link, type, date)
                with st.expander(f"{'🎥' if item[2]=='Video' else '📄'} {item[0]}"):
                    if item[2] == "Video":
                        st.video(item[1])
                    else:
                        st.markdown(f"**[Download PDF]({item[1]})**")
                    st.caption(f"Uploaded on: {item[3]}")
        else:
            st.info("No content found matching filters.")

    elif menu == "👤 Profile":
        st.title("Profile Settings")
        st.write(f"**Username:** {st.session_state.user_info['username']}")
        st.write(f"**Name:** {st.session_state.user_info['name']}")
        st.info("Edit Profile feature coming in v2.0")

# --- C. ADMIN DASHBOARD ---
def admin_dashboard():
    with st.sidebar:
        st.title("👮 Admin Panel")
        menu = st.radio("Controls", ["Upload Manager", "User Database", "System Logs"])
        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    if menu == "Upload Manager":
        st.header("📤 Upload Content")
        
        with st.form("upload_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            u_cat = col1.selectbox("Category", ["DSC", "GE", "VAC", "AEC", "SEC", "Other"])
            u_type = col2.radio("Content Type", ["Video", "PDF Notes", "PYQ"])
            
            u_stream = st.text_input("Stream Name (e.g. B.Com Hons)")
            u_sub = st.text_input("Subject Name (e.g. Corporate Law)")
            u_title = st.text_input("Title")
            u_link = st.text_input("Link (YouTube/Drive)")
            
            if st.form_submit_button("Upload to App"):
                if u_stream and u_sub and u_title and u_link:
                    C.execute("INSERT INTO courses (category, stream, subject, title, link, type, uploaded_by, date) VALUES (?,?,?,?,?,?,?,?)",
                              (u_cat, u_stream, u_sub, u_title, u_link, u_type, st.session_state.user_info['username'], str(datetime.now().date())))
                    CONN.commit()
                    st.success("Uploaded Successfully!")
                    log_activity(st.session_state.user_info['username'], "Upload", f"Uploaded {u_title}")
                else:
                    st.error("Please fill all fields")

    elif menu == "User Database":
        st.header("👥 Registered Students")
        users_df = pd.read_sql_query("SELECT username, name, role, mobile, joined_at FROM users", CONN)
        st.dataframe(users_df, use_container_width=True)

    elif menu == "System Logs":
        st.header("📜 Activity Logs")
        logs_df = pd.read_sql_query("SELECT * FROM activity ORDER BY id DESC", CONN)
        st.dataframe(logs_df, use_container_width=True)

# ==========================================
# 6. MAIN CONTROLLER
# ==========================================
if not st.session_state.logged_in:
    auth_screen()
else:
    if st.session_state.user_info['role'] == 'admin':
        admin_dashboard()
    else:
        student_dashboard()
# ==========================================
# 7. APP FOOTER (COPYRIGHT & CREDITS)
# ==========================================
# Yeh code har page ke niche copyright dikhayega (Login ke alawa)
if st.session_state.logged_in:
    st.markdown("""
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: white;
            color: grey;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            border-top: 1px solid #e1e4e8;
        }
    </style>
    <div class="footer">
        <p>© 2026 Edu Sharks LMS | Designed for Delhi University Students | Version 2.0 Pro</p>
    </div>
    """, unsafe_allow_html=True)

# --- DATABASE CONNECTION CLOSE (Safety) ---
# Jab app ruk jaye to connection close kar do taaki database corrupt na ho
# Note: Streamlit mein ise handle karna mushkil hota hai, par yeh clean practice hai.
def on_shutdown():
    CONN.close()
