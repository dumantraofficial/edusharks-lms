import streamlit as st
import json
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Edu Sharks LMS", layout="wide", page_icon="🦈")

# --- DATABASE FUNCTION (JSON SE BAAT KARNE KE LIYE) ---
DB_FILE = "courses.json"

def load_data():
    # Agar file nahi mili, to empty structure bana dega
    if not os.path.exists(DB_FILE):
        return {"DSC": {}, "GE": {}, "VAC": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- SESSION STATE ---
if 'user_type' not in st.session_state:
    st.session_state.user_type = None  # 'student' or 'admin'

# ==========================================
# 🔐 MAIN LOGIN SCREEN
# ==========================================
if st.session_state.user_type is None:
    st.markdown("<h1 style='text-align: center;'>🦈 Edu Sharks LMS</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # STUDENT LOGIN
    with col1:
        with st.container(border=True):
            st.header("👨‍🎓 Student Login")
            if st.button("Login as Student", use_container_width=True):
                st.session_state.user_type = "student"
                st.rerun()

    # ADMIN LOGIN
    with col2:
        with st.container(border=True):
            st.header("👮 Admin Login")
            admin_pass = st.text_input("Admin Password", type="password")
            if st.button("Enter Admin Panel", use_container_width=True):
                if admin_pass == "admin123":  # Admin Password
                    st.session_state.user_type = "admin"
                    st.rerun()
                else:
                    st.error("Wrong Password!")

# ==========================================
# 👨‍🎓 STUDENT DASHBOARD
# ==========================================
elif st.session_state.user_type == "student":
    course_data = load_data() # JSON se data load kiya
    
    with st.sidebar:
        st.title("👤 Student Panel")
        if st.button("Logout"):
            st.session_state.user_type = None
            st.rerun()
    
    st.title("🎓 My Classroom")
    
    # 1. Category Select
    category = st.selectbox("Select Category", ["Select..."] + list(course_data.keys()))
    
    if category != "Select...":
        # 2. Stream Select
        streams = list(course_data.get(category, {}).keys())
        stream = st.selectbox("Select Stream", ["Select..."] + streams)
        
        if stream != "Select...":
            # 3. Subject Select
            subjects = list(course_data[category][stream].keys())
            subject = st.selectbox("Select Subject", ["Select..."] + subjects)
            
            if subject != "Select...":
                st.divider()
                st.subheader(f"📺 Content: {subject}")
                
                # Content Show Karega
                content_list = course_data[category][stream][subject]
                
                if not content_list:
                    st.warning("No videos uploaded yet.")
                
                for item in content_list:
                    with st.expander(f"🎥 {item['title']}"):
                        st.video(item['link'])

# ==========================================
# 👮 ADMIN PANEL (UPLOAD SYSTEM)
# ==========================================
elif st.session_state.user_type == "admin":
    course_data = load_data()
    
    with st.sidebar:
        st.title("👮 Admin Panel")
        st.info("Add new courses and videos here.")
        if st.button("Logout"):
            st.session_state.user_type = None
            st.rerun()

    st.header("📤 Upload Content Manager")
    
    tab1, tab2 = st.tabs(["Add New Video", "Create New Subject"])
    
    # --- TAB 1: ADD VIDEO ---
    with tab1:
        st.subheader("Add Video to Existing Subject")
        
        # Selection Chain
        a_cat = st.selectbox("Category", list(course_data.keys()), key="a_cat")
        
        # Stream nikalna
        available_streams = list(course_data.get(a_cat, {}).keys())
        a_stream = st.selectbox("Stream", available_streams, key="a_stream") if available_streams else None
        
        # Subject nikalna
        available_subs = []
        if a_stream:
            available_subs = list(course_data[a_cat][a_stream].keys())
        a_sub = st.selectbox("Subject", available_subs, key="a_sub") if available_subs else None
        
        st.divider()
        
        # Upload Form
        with st.form("upload_video"):
            v_title = st.text_input("Video Title (e.g., Unit 1)")
            v_link = st.text_input("YouTube Link")
            submit = st.form_submit_button("Upload Video 🚀")
            
            if submit and a_sub and v_title and v_link:
                new_video = {"title": v_title, "type": "video", "link": v_link}
                
                # Data Save karna JSON mein
                course_data[a_cat][a_stream][a_sub].append(new_video)
                save_data(course_data)
                
                st.success(f"Video '{v_title}' Added Successfully!")
                
    # --- TAB 2: CREATE NEW SUBJECT ---
    with tab2:
        st.subheader("Create New Subject Folder")
        
        n_cat = st.selectbox("Select Category", list(course_data.keys()), key="n_cat")
        n_stream = st.text_input("Stream Name (e.g., BA (Arts) or BBA)")
        n_sub = st.text_input("Subject Name (e.g., History Hons)")
        
        if st.button("Create Folder"):
            if n_stream and n_sub:
                if n_stream not in course_data[n_cat]:
                    course_data[n_cat][n_stream] = {}
                
                if n_sub not in course_data[n_cat][n_stream]:
                    course_data[n_cat][n_stream][n_sub] = []
                    save_data(course_data)
                    st.success(f"Created: {n_stream} -> {n_sub}")
                    st.rerun()
                else:
                    st.warning("Subject already exists!")