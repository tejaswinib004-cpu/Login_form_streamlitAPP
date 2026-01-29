import streamlit as st
import mysql.connector
from mysql.connector import Error
import re
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="User Authentication System",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling and animations
st.markdown("""
    <style>
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0px);
        }
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(-20px);
            opacity: 0;
        }
        to {
            transform: translateX(0px);
            opacity: 1;
        }
    }
    
    .main-container {
        animation: fadeIn 0.8s ease-in-out;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .success-message {
        animation: slideIn 0.6s ease-in-out;
    }
    
    .form-container {
        animation: fadeIn 1s ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

# Database configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "student_db"
DB_TABLE = "users"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'

# Database Functions
def get_db_connection():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Error as e:
        st.error(f"❌ Database Connection Error: {e}")
        return None

def create_users_table():
    """Create users table if it doesn't exist"""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"❌ Error creating table: {e}")
        return False

def register_user(username, email, password, confirm_password):
    """Register a new user"""
    # Validation
    if not username or not email or not password:
        st.warning("⚠️ Please fill all fields")
        return False
    
    if len(username) < 3:
        st.warning("⚠️ Username must be at least 3 characters long")
        return False
    
    if len(password) < 6:
        st.warning("⚠️ Password must be at least 6 characters long")
        return False
    
    if password != confirm_password:
        st.warning("⚠️ Passwords do not match")
        return False
    
    # Email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        st.warning("⚠️ Please enter a valid email address")
        return False
    
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        insert_query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, email, password))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Success animation
        with st.spinner(''):
            time.sleep(1)
        
        return True
    except mysql.connector.errors.IntegrityError as e:
        if "username" in str(e).lower():
            st.error("❌ Username already exists")
        elif "email" in str(e).lower():
            st.error("❌ Email already registered")
        else:
            st.error(f"❌ Registration error: {e}")
        return False
    except Error as e:
        st.error(f"❌ Database error: {e}")
        return False

def login_user(username, password):
    """Authenticate user login"""
    if not username or not password:
        st.warning("⚠️ Please enter username and password")
        return False
    
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        query = "SELECT id, username FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            return True
        else:
            st.error("❌ Invalid username or password")
            return False
    except Error as e:
        st.error(f"❌ Login error: {e}")
        return False

def get_user_count():
    """Get total number of registered users"""
    try:
        conn = get_db_connection()
        if conn is None:
            return 0
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Error:
        return 0

# Main Application
def main():
    # Create users table on app startup
    create_users_table()
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #667eea;'>🔐 Secure Auth</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Login or Register to Continue</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar for switching modes
    with st.sidebar:
        st.markdown("### 📋 Navigation")
        mode = st.radio("Choose an option:", ["🔑 Login", "📝 Register"], key="auth_mode_radio")
        
        # Show stats
        st.markdown("---")
        st.markdown("### 📊 Stats")
        user_count = get_user_count()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Users", user_count)
        with col2:
            st.metric("Status", "Online" if st.session_state.logged_in else "Offline")
    
    # Main content area
    if st.session_state.logged_in:
        # Header Navigation
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        with col1:
            if st.button("🏠 Home", use_container_width=True, key="nav_home"):
                st.session_state.page = "home"
        with col2:
            if st.button("👤 Profile", use_container_width=True, key="nav_profile"):
                st.session_state.page = "profile"
        with col3:
            if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
                st.session_state.page = "dashboard"
        with col4:
            if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
                st.session_state.page = "settings"
        with col5:
            if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.success("✅ Logged out successfully!")
                time.sleep(1)
                st.rerun()
        
        st.markdown("---")
        
        # Initialize page state
        if 'page' not in st.session_state:
            st.session_state.page = "home"
        
        # HOME PAGE
        if st.session_state.page == "home":
            st.markdown(f"""
            <div style='text-align: center; padding: 30px;'>
                <h1 style='color: #667eea; font-size: 48px;'>Welcome Back! 👋</h1>
                <h2 style='color: #764ba2;'>{st.session_state.username}</h2>
                <p style='font-size: 18px; color: #666;'>You are now authenticated and can access all features</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.balloons()
            
            # Feature Cards
            st.markdown("### 🌟 Featured Services")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 20px; border-radius: 10px; text-align: center; color: white;'>
                    <h3>📚 Learning Hub</h3>
                    <p>Access educational resources and tutorials</p>
                    <button style='background-color: white; color: #667eea; padding: 10px 20px; 
                                   border: none; border-radius: 5px; cursor: pointer; font-weight: bold;'>
                        Explore
                    </button>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            padding: 20px; border-radius: 10px; text-align: center; color: white;'>
                    <h3>🎯 Tasks & Projects</h3>
                    <p>Manage your daily tasks and projects efficiently</p>
                    <button style='background-color: white; color: #f5576c; padding: 10px 20px; 
                                   border: none; border-radius: 5px; cursor: pointer; font-weight: bold;'>
                        View Tasks
                    </button>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                            padding: 20px; border-radius: 10px; text-align: center; color: white;'>
                    <h3>🔔 Notifications</h3>
                    <p>Stay updated with real-time notifications</p>
                    <button style='background-color: white; color: #00f2fe; padding: 10px 20px; 
                                   border: none; border-radius: 5px; cursor: pointer; font-weight: bold;'>
                        Check Now
                    </button>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Quick Stats
            st.markdown("### 📈 Your Activity")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sessions", "24", "+3 this week")
            with col2:
                st.metric("Tasks Completed", "156", "+12 this month")
            with col3:
                st.metric("Learning Hours", "48", "+5 this week")
            with col4:
                st.metric("Achievements", "12", "+2 new")
            
            st.markdown("---")
            
            # Recent Activity
            st.markdown("### 📝 Recent Activity")
            activities = [
                {"emoji": "✅", "activity": "Completed Python Basics Course", "time": "2 hours ago"},
                {"emoji": "📝", "activity": "Submitted Project Assignment", "time": "5 hours ago"},
                {"emoji": "🏆", "activity": "Earned 'Expert Developer' Badge", "time": "1 day ago"},
                {"emoji": "💬", "activity": "Commented on Discussion Forum", "time": "2 days ago"},
            ]
            
            for activity in activities:
                st.info(f"{activity['emoji']} {activity['activity']} • {activity['time']}")
        
        # PROFILE PAGE
        elif st.session_state.page == "profile":
            st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='color: #667eea;'>👤 User Profile</h1>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("""
                <div style='text-align: center;'>
                    <div style='width: 150px; height: 150px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                border-radius: 50%; margin: auto; display: flex; align-items: center; justify-content: center;
                                font-size: 60px;'>
                        👤
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='padding: 20px;'>
                    <h2>Username</h2>
                    <p style='font-size: 18px; color: #667eea;'><strong>{st.session_state.username}</strong></p>
                    <h2>Account Status</h2>
                    <p style='font-size: 18px; color: green;'>✅ <strong>Active</strong></p>
                    <h2>Member Since</h2>
                    <p style='font-size: 18px;'><strong>{datetime.now().strftime('%B %d, %Y')}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 📋 Profile Information")
            
            col1, col2 = st.columns(2)
            with col1:
                email_display = st.text_input("📧 Email", value="user@example.com", disabled=True)
            with col2:
                phone_display = st.text_input("📱 Phone", value="+1 (555) 123-4567", disabled=True)
            
            col1, col2 = st.columns(2)
            with col1:
                country = st.text_input("🌍 Country", value="United States", disabled=True)
            with col2:
                city = st.text_input("🏙️ City", value="New York", disabled=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Edit Profile", use_container_width=True):
                    st.info("Edit profile feature coming soon!")
            with col2:
                if st.button("🔐 Change Password", use_container_width=True):
                    st.warning("Password change feature coming soon!")
        
        # DASHBOARD PAGE
        elif st.session_state.page == "dashboard":
            st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='color: #667eea;'>📊 Dashboard</h1>
            </div>
            """, unsafe_allow_html=True)
            
            # Dashboard stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div style='background: #E8EAF6; padding: 20px; border-radius: 10px; text-align: center;'>
                    <h3 style='color: #667eea;'>📊 Total Views</h3>
                    <h1 style='color: #667eea; font-size: 36px;'>2,547</h1>
                    <p style='color: green;'>↑ 12% from last month</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background: #FCE4EC; padding: 20px; border-radius: 10px; text-align: center;'>
                    <h3 style='color: #f5576c;'>👥 New Users</h3>
                    <h1 style='color: #f5576c; font-size: 36px;'>384</h1>
                    <p style='color: green;'>↑ 8% from last month</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style='background: #E0F2F1; padding: 20px; border-radius: 10px; text-align: center;'>
                    <h3 style='color: #00f2fe;'>💰 Revenue</h3>
                    <h1 style='color: #00f2fe; font-size: 36px;'>$12.5K</h1>
                    <p style='color: green;'>↑ 23% from last month</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div style='background: #FFF3E0; padding: 20px; border-radius: 10px; text-align: center;'>
                    <h3 style='color: #FF9800;'>⭐ Rating</h3>
                    <h1 style='color: #FF9800; font-size: 36px;'>4.8</h1>
                    <p style='color: green;'>↑ 0.3 from last month</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Chart data
            st.markdown("### 📈 Performance Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Weekly Activity")
                activity_data = {
                    "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                    "Users": [120, 150, 180, 160, 200, 140, 100]
                }
                st.line_chart(data=activity_data, x="Day", y="Users")
            
            with col2:
                st.markdown("#### Category Distribution")
                category_data = {
                    "Category": ["Product A", "Product B", "Product C", "Product D"],
                    "Sales": [45, 30, 20, 5]
                }
                st.bar_chart(data=category_data, x="Category", y="Sales")
        
        # SETTINGS PAGE
        elif st.session_state.page == "settings":
            st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='color: #667eea;'>⚙️ Settings</h1>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🔔 Notifications")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Email Notifications")
            with col2:
                st.toggle("Enable", value=True, key="email_notif")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Push Notifications")
            with col2:
                st.toggle("Enable", value=True, key="push_notif")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("SMS Alerts")
            with col2:
                st.toggle("Enable", value=False, key="sms_notif")
            
            st.markdown("---")
            
            st.markdown("### 🎨 Appearance")
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], key="theme_select")
            st.info(f"Selected theme: {theme}")
            
            st.markdown("---")
            
            st.markdown("### 🔐 Privacy & Security")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Two-Factor Authentication")
            with col2:
                st.toggle("Enable", value=False, key="2fa_toggle")
            
            st.markdown("---")
            
            st.markdown("### 💾 Data Management")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Download My Data", use_container_width=True):
                    st.success("✅ Download started!")
            with col2:
                if st.button("🗑️ Delete Account", use_container_width=True):
                    st.error("❌ Account deletion requires confirmation")
            
            st.markdown("---")
            
            if st.button("💾 Save Settings", use_container_width=True):
                st.success("✅ Settings saved successfully!")
    
    else:
        # Login/Register forms
        if "🔑 Login" in mode:
            st.subheader("🔑 User Login")
            with st.form("login_form", clear_on_submit=True):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit_btn = st.form_submit_button("🔓 Login", use_container_width=True)
                with col2:
                    st.form_submit_button("Clear", use_container_width=True)
            
            if submit_btn:
                with st.spinner('🔍 Verifying credentials...'):
                    time.sleep(1)
                    if login_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("✅ Login Successful!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
        
        else:  # Register mode
            st.subheader("📝 Create New Account")
            with st.form("register_form", clear_on_submit=True):
                username = st.text_input("👤 Username", placeholder="Choose a username (min 3 chars)")
                email = st.text_input("📧 Email", placeholder="Enter your email address")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter password (min 6 chars)")
                confirm_password = st.text_input("🔐 Confirm Password", type="password", placeholder="Confirm your password")
                
                # Password strength indicator
                if password:
                    strength = len(password)
                    if strength < 6:
                        st.warning("⚠️ Password is too weak")
                    elif strength < 10:
                        st.info("ℹ️ Password strength: Medium")
                    else:
                        st.success("✅ Password strength: Strong")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit_btn = st.form_submit_button("✍️ Register", use_container_width=True)
                with col2:
                    st.form_submit_button("Clear", use_container_width=True)
            
            if submit_btn:
                with st.spinner('📝 Creating account...'):
                    time.sleep(1)
                    if register_user(username, email, password, confirm_password):
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            st.success("✅ Registration Successful!")
                            st.balloons()
                        st.info("💡 You can now login with your credentials")
                        time.sleep(2)
                        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #999; font-size: 12px;'>
        <p>🔐 Secure Authentication System | Built with Streamlit & MySQL</p>
        <p>© 2026 All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()