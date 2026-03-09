import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import json, pathlib
import random
import pandas as pd
import numpy as np
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ======================================
# 🔐 GOOGLE AUTH SETUP
# ======================================
def google_login():
    import streamlit as st
    from google_auth_oauthlib.flow import Flow
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    import requests
    import urllib.parse
    import os

    # === CONFIG ===
    # Use the dictionary from secrets, NOT a physical file
    client_config = dict(st.secrets["google_secrets"])
    redirect_uri = st.secrets["REDIRECT_URI"]

    # === CREATE FLOW ===
    # CHANGED: Use from_client_config to read from Streamlit Secrets
    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
        ],
        redirect_uri=redirect_uri,
    )

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # === STEP 1: User not logged in yet ===
    if "credentials" not in st.session_state and "code" not in st.query_params:
        auth_url, _ = flow.authorization_url(prompt="consent", include_granted_scopes="true")
        st.markdown(
            f"""
            <div style='text-align:center; margin-top:100px'>
                <h2>🔐 Login with Google</h2>
                <a href="{auth_url}" target="_self">
                    <button style="padding:12px 24px; border:none; border-radius:8px;
                    background:linear-gradient(135deg,#4285F4,#34A853,#FBBC05,#EA4335);
                    color:white; font-weight:bold; cursor:pointer;">Sign in with Google</button>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    # === STEP 2: Returned from Google ===
    if "code" in st.query_params and "credentials" not in st.session_state:
        try:
            # Manually reconstruct the full callback URL with parameters
            # This ensures the 'state' and 'code' match what Google expects
            params = st.query_params.to_dict()
            query_str = urllib.parse.urlencode(params)
            full_url = f"{redirect_uri}?{query_str}"

            # Pass the full URL to fetch_token
            flow.fetch_token(authorization_response=full_url)
            credentials = flow.credentials

            # Verify and decode ID token
            request = google_requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, request, client_config["web"]["client_id"]
            )

            # === FIREBASE AUTH ===
            FIREBASE_WEB_API_KEY = st.secrets.get("FIREBASE_KEY", "AIzaSyCrcpDkftxIsBGK9BVkVghX7C0qX9iJS74") 
            firebase_auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_WEB_API_KEY}"
            
            payload = {
                "postBody": f"id_token={credentials.id_token}&providerId=google.com",
                "requestUri": redirect_uri, # CHANGED: Must match your actual deployed URL
                "returnIdpCredential": True,
                "returnSecureToken": True
            }
            
            fb_response = requests.post(firebase_auth_url, json=payload)
            firebase_data = fb_response.json()
            
            if "error" in firebase_data:
                st.error(f"❌ Firebase Auth Failed: {firebase_data['error']['message']}")
                st.stop()

            # Save info to session
            st.session_state.credentials = id_info
            st.session_state.firebase_token = firebase_data.get('idToken') 
            
            st.query_params.clear() 
            st.rerun()

        except Exception as e:
            st.error(f"❌ Login failed: {e}")
            st.stop()

    return st.session_state.get("credentials")


# ======================================

# 🚀 RUN LOGIN BEFORE APP LOADS

# ======================================

user = google_login()
if user:
    st.sidebar.image(user["picture"], width=60)
    st.sidebar.success(f"👋 Welcome, {user['name']}")
    st.sidebar.caption(user["email"])

    if st.sidebar.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
else:
    st.stop()

# --- Enhanced Custom CSS for Modern UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .metric-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        padding: 24px;
        border-radius: 20px;
        margin: 15px 0;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    .metric-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        border-radius: 20px 20px 0 0;
    }
    
    .status-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .status-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .critical-alert {
        background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%);
        border-left-color: #dc2626;
        color: #991b1b;
    }
    
    .warning-alert {
        background: linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%);
        border-left-color: #d97706;
        color: #92400e;
    }
    
    .success-alert {
        background: linear-gradient(135deg, #d1fae5 0%, #f0fdf4 100%);
        border-left-color: #059669;
        color: #065f46;
    }
    
    .info-alert {
        background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%);
        border-left-color: #2563eb;
        color: #1d4ed8;
    }
    
    .interactive-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        color: white !important;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .interactive-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Fix Streamlit button text visibility */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%) !important;
    }
    
    .stButton > button:focus {
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.5) !important;
        outline: none !important;
    }
    
    /* Fix selectbox text visibility */
    .stSelectbox > div > div {
        background-color: white !important;
        color: #1e293b !important;
    }
    
    /* Fix slider text */
    .stSlider > div > div > div {
        color: #1e293b !important;
    }
    
    /* ============================================
       🔧 COMPREHENSIVE TEXT VISIBILITY FIXES
       Stronger CSS selectors to override Streamlit defaults
       ============================================ */
    
    /* Force button text visibility with highest specificity */
    div.stButton > button, 
    .stButton button,
    button[kind="primary"],
    button[kind="secondary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        text-shadow: none !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    }
    
    div.stButton > button:hover,
    .stButton button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Sidebar button text fixes */
    .stSidebar div.stButton > button,
    .stSidebar .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        width: 100% !important;
        margin: 2px 0 !important;
    }
    
    /* Fix selectbox text */
    .stSelectbox > div > div > div,
    .stSelectbox label,
    .stSelectbox div[role="button"],
    .stSelectbox div[data-baseweb="select"] {
        color: #1f2937 !important;
        background-color: white !important;
    }
    
    /* Fix all form labels */
    .stSelectbox label,
    .stSlider label,
    .stCheckbox label,
    .stNumberInput label,
    .stTextInput label {
        color: #374151 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }
    
    /* Fix slider text and values */
    .stSlider div[data-testid="stSlider"] div,
    .stSlider span,
    .stSlider p {
        color: #1f2937 !important;
    }
    
    /* Fix checkbox text */
    .stCheckbox > label > div,
    .stCheckbox span {
        color: #1f2937 !important;
    }
    
    /* Fix sidebar headers */
    .stSidebar h1,
    .stSidebar h2,
    .stSidebar h3,
    .stSidebar h4,
    .stSidebar .stMarkdown h1,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3,
    .stSidebar .stMarkdown h4 {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }
    
    /* Fix main content text */
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4,
    h1, h2, h3, h4 {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }
    
    .stMarkdown p,
    .stMarkdown div,
    p, div {
        color: #374151 !important;
    }
    
    /* Fix metric text */
    div[data-testid="metric-container"] > div,
    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] div {
        color: #1f2937 !important;
    }
    
    /* Fix tab text with extreme specificity */
    .stTabs [data-baseweb="tab"] > div,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] p,
    .stTabs button[role="tab"] > div,
    .stTabs button[role="tab"] span {
        color: #64748b !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }
    
    .stTabs [aria-selected="true"] > div,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] p,
    .stTabs button[role="tab"][aria-selected="true"] > div,
    .stTabs button[role="tab"][aria-selected="true"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Force visibility for any remaining text elements */
    * {
        text-shadow: none !important;
    }
    
    .stApp {
        color: #374151 !important;
    }
    
    .fleet-card {
        background: white;
        border-radius: 16px;
        padding: 16px;
        margin: 8px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
    }
    
    .fleet-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-available { background: #d1fae5; color: #065f46; }
    .status-working { background: #dbeafe; color: #1e40af; }
    .status-failed { background: #fee2e2; color: #991b1b; }
    .status-charging { background: #fef3c7; color: #92400e; }
    
    .pulse-animation {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: .7; }
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* ============================================
       🎨 TAB COLOR CUSTOMIZATION SECTION
       Change these values to customize tab colors
       ============================================ */
    
    /* OPTION 1: Blue Theme (Current) 
    :root {
        --tab-active-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --tab-active-shadow: rgba(102, 126, 234, 0.4);
        --tab-hover-bg: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
        --tab-hover-shadow: rgba(124, 58, 237, 0.5);
    }*/
    
    OPTION 2: Green Theme - Uncomment to use
    :root {
        --tab-active-bg: linear-gradient(135deg, #059669 0%, #10b981 100%);
        --tab-active-shadow: rgba(5, 150, 105, 0.4);
        --tab-hover-bg: linear-gradient(135deg, #047857 0%, #059669 100%);
        --tab-hover-shadow: rgba(4, 120, 87, 0.5);
    }
    
    
    /* OPTION 3: Orange Theme - Uncomment to use
    :root {
        --tab-active-bg: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
        --tab-active-shadow: rgba(234, 88, 12, 0.4);
        --tab-hover-bg: linear-gradient(135deg, #c2410c 0%, #ea580c 100%);
        --tab-hover-shadow: rgba(194, 65, 12, 0.5);
    }
    */
    
    /* OPTION 4: Pink Theme - Uncomment to use
    :root {
        --tab-active-bg: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
        --tab-active-shadow: rgba(236, 72, 153, 0.4);
        --tab-hover-bg: linear-gradient(135deg, #db2777 0%, #ec4899 100%);
        --tab-hover-shadow: rgba(219, 39, 119, 0.5);
    }
    */
    
    /* OPTION 5: Teal Theme - Uncomment to use
    :root {
        --tab-active-bg: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
        --tab-active-shadow: rgba(8, 145, 178, 0.4);
        --tab-hover-bg: linear-gradient(135deg, #0e7490 0%, #0891b2 100%);
        --tab-hover-shadow: rgba(14, 116, 144, 0.5);
    }
    */
    
    /* Apply the custom colors to tabs */
    .stTabs [aria-selected="true"] {
        background: var(--tab-active-bg) !important;
        color: white !important;
        border-color: transparent;
        box-shadow: 0 6px 20px var(--tab-active-shadow);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"]:hover {
        background: var(--tab-hover-bg) !important;
        color: white !important;
        box-shadow: 0 8px 25px var(--tab-hover-shadow);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border-radius: 12px;
        color: #64748b !important;
        font-weight: 500;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%);
        border-color: #cbd5e1;
        transform: translateY(-1px);
        color: #374151 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: transparent;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%) !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5);
    }
    
    /* Tab text styling */
    .stTabs [data-baseweb="tab"] div {
        color: inherit !important;
        font-weight: inherit !important;
        text-transform: none !important;
        letter-spacing: 0.025em;
    }
    
    .stSidebar > div {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    .stSidebar .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin: 4px 0 !important;
    }
    
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%) !important;
        transform: translateY(-1px) !important;
    }
    
    .control-section {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .map-container {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .dataframe-container {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    .log-container {
        background: #1e293b;
        color: #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 13px;
        line-height: 1.5;
        max-height: 400px;
        overflow-y: auto;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .performance-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
        margin: 4px 0;
    }
    
    .perf-excellent { background: #d1fae5; color: #065f46; }
    .perf-good { background: #dbeafe; color: #1e40af; }
    .perf-warning { background: #fef3c7; color: #92400e; }
    .perf-critical { background: #fee2e2; color: #991b1b; }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="AGV Fleet Management System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AGV, Task, Warehouse Classes ---
class AGV:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.batterylevel = random.uniform(60, 100)
        self.failed = False
        self.faulttype = None
        self.faultseverity = 0
        self.task = None
        self.losttask = None
        self.taskcompletioncount = 0
        self.totaldistance = 0
        self.lastmaintenance = time.time()
        self.operatinghours = random.uniform(0, 1000)
        self.intercept_info = None
        # 🆕 NEW: Add a list to track the last 5 positions for a movement trail
        self.path_history = [(x, y)] 

    def move(self):
        if self.failed or not self.task:
            return None
            
        dx = self.task.x - self.x
        dy = self.task.y - self.y
        
        if abs(dx) > 0: self.x += 1 if dx > 0 else -1
        if abs(dy) > 0: self.y += 1 if dy > 0 else -1
            
        self.totaldistance += 1
        self.batterylevel -= 0.1
        
        # 🆕 NEW: Record position for the trail
        self.path_history.append((self.x, self.y))
        # Keep only the last 6 steps so the map doesn't get cluttered
        if len(self.path_history) > 6:
            self.path_history.pop(0)
            
        if self.x == self.task.x and self.y == self.task.y:
            completed_task = self.task
            self.task = None
            self.taskcompletioncount += 1
            completed_task.completed = True
            
            if hasattr(self, 'intercept_info'):
                self.intercept_info = None
            
            # 🆕 NEW: Clear history when task is done to avoid dragging a line across the map
            self.path_history = [(self.x, self.y)]
                
            return completed_task
            
        return None
    
    def inducefault(self, log, tasks, fleet, assignment_system):
        if not self.failed and random.random() < 0.02:  # 2% chance
            self.failed = True
            self.faulttype = random.choice(["LiDAR Error", "Battery Crit", "Motor Jam"])
        
        if self.task:
            self.losttask = self.task
            # Log the failure first
            log.append(f"🚨 AGV-{self.id:03d} FAILED ({self.faulttype}) while on T-{self.losttask.id}")
            
            # Immediately attempt the Dynamic Takeover
            assignment_system.trigger_immediate_takeover(self, fleet, log)
            self.task = None # Original AGV drops the task
        else:
            log.append(f"🚨 AGV-{self.id:03d} FAILED ({self.faulttype})")
    
    def autorecover(self, log):
        if self.failed and self.faultseverity <= 2 and random.random() < 0.15:  # 15% auto-recovery chance
            self.failed = False
            log.append(f"✅ AGV-{self.id:03d} AUTO-RECOVERY: {self.faulttype} fault resolved")
            self.faulttype = None
            self.faultseverity = 0
            self.losttask = None
    
    def manualrecover(self, log):
        if self.failed:
            self.failed = False
            log.append(f"🔧 AGV-{self.id:03d} MANUAL RECOVERY: {self.faulttype} fault manually resolved")
            self.faulttype = None
            self.faultseverity = 0
            self.losttask = None
    
    def gethealthscore(self):
        score = 100
        if self.failed:
            score -= self.faultseverity * 20
        score -= max(0, (100 - self.batterylevel) * 0.5)
        score -= min(30, self.operatinghours * 0.01)
        return max(0, score)

class Task:
    def __init__(self, id, x, y, priority=1, deadline=None):
        self.id = id
        self.x = x
        self.y = y
        self.priority = priority
        self.deadline = deadline or (time.time() + 1800)
        self.assignedagvid = None
        self.reassignmentcount = 0
        self.completed = False
        self.createdtime = time.time()

class TaskAssignmentSystem:
    def trigger_immediate_takeover(self, failed_agv, fleet, log):
        # 1. Identify healthy, idle AGVs to help
        candidates = [a for a in fleet if not a.failed and not a.task and a.id != failed_agv.id]
        
        if candidates:
            # 2. Pick the closest AGV to the failure site
            best_backup = min(candidates, key=lambda a: abs(a.x - failed_agv.x) + abs(a.y - failed_agv.y))
            
            # 3. Transfer the task details
            best_backup.task = failed_agv.losttask
            best_backup.task.assignedagvid = best_backup.id
            
            # 4. Set the link info for UI (matches your image history)
            best_backup.intercept_info = f"Recovering T-{best_backup.task.id} from failed AGV-{failed_agv.id:03d}"
            
            log.append(f"⚡ DYNAMIC TAKEOVER: AGV-{best_backup.id:03d} is now doing failed AGV-{failed_agv.id:03d}'s Task T-{best_backup.task.id}")
            
            failed_agv.losttask = None
            return True # Fixed Indentation
            
        # If no one is available
        log.append(f"⚠️ TAKEOVER FAILED: No idle AGVs available to help AGV-{failed_agv.id:03d}")
        return False # Fixed Indentation
        
    def smarttaskassignment(self, tasks, agvs, log):
        assignments = 0
        unassigned_tasks = [t for t in tasks if not t.assignedagvid and not t.completed]
        available_agvs = [a for a in agvs if not a.failed and not a.task]
        
        # Sort tasks by priority and deadline
        unassigned_tasks.sort(key=lambda t: (t.priority, t.deadline))
        
        for task in unassigned_tasks:
            if not available_agvs:
                break
                
            # Find best AGV (closest with highest battery)
            best_agv = min(available_agvs, key=lambda agv: 
                ((agv.x - task.x)**2 + (agv.y - task.y)**2) - agv.batterylevel/10)
            
            task.assignedagvid = best_agv.id
            best_agv.task = task
            available_agvs.remove(best_agv)
            assignments += 1
            
            if task.reassignmentcount > 0:
                log.append(f"🔄 REASSIGNMENT: Task T-{task.id} assigned to AGV-{best_agv.id:03d} (attempt #{task.reassignmentcount + 1})")
            else:
                log.append(f"📋 Task T-{task.id} assigned to AGV-{best_agv.id:03d}")
                
        return assignments
    
    def recoverlosttasks(self, agvs, log):
        recovered = 0
        for agv in agvs:
            if agv.losttask and not agv.failed:
                agv.task = agv.losttask
                agv.losttask.assignedagvid = agv.id
                agv.losttask = None
                recovered += 1
                log.append(f"🔄 Task T-{agv.task.id} recovered by AGV-{agv.id:03d}")
        return recovered

class WarehouseSystem:
    def __init__(self):
        self.taskassignmentsystem = TaskAssignmentSystem()
    
    def calculatekpis(self, agvs, tasks):
        total_agvs = len(agvs)
        operational_agvs = sum(1 for agv in agvs if not agv.failed)
        availability = (operational_agvs / total_agvs) * 100 if total_agvs > 0 else 0
        
        avg_battery = sum(agv.batterylevel for agv in agvs) / total_agvs if total_agvs > 0 else 0
        
        total_reassignments = sum(task.reassignmentcount for task in tasks)
        total_tasks = len(tasks)
        reassignment_rate = (total_reassignments / total_tasks) * 100 if total_tasks > 0 else 0
        
        completed_tasks = sum(1 for task in tasks if task.completed)
        efficiency = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        network_health = sum(1 for agv in agvs if not agv.failed and agv.faulttype != "Communication") / total_agvs * 100
        
        pending_tasks = sum(1 for task in tasks if not task.assignedagvid and not task.completed)
        
        return {
            'availability': availability,
            'avgbattery': avg_battery,
            'reassignmentrate': reassignment_rate,
            'efficiency': efficiency,
            'networkhealth': network_health,
            'pendingtasks': pending_tasks
        }

# --- System Initialization ---
GRIDSIZE = 25
NUMAGVS = 8
NUMTASKS = 15

if 'agvs' not in st.session_state:
    st.session_state.agvs = [AGV(i, random.randint(0, GRIDSIZE), random.randint(0, GRIDSIZE)) for i in range(NUMAGVS)]
    st.session_state.tasks = [Task(i, random.randint(0, GRIDSIZE), random.randint(0, GRIDSIZE), 
                                  random.choice([1,2,3]), time.time()+random.randint(300,1800)) for i in range(NUMTASKS)]
    st.session_state.warehouse = WarehouseSystem()
    st.session_state.log = []
    st.session_state.autorun = False
    st.session_state.GRIDSIZE = GRIDSIZE
    st.session_state.stepcount = 0
    st.session_state.kpihistory = []
    st.session_state.completedtasks = []
    st.session_state.enhancedsystem = True

# --- Header ---
st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🤖 AGV Fleet Management System</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Intelligent Autonomous Vehicle Fleet Operations & Real-time Monitoring</p>
    </div>
""", unsafe_allow_html=True)

# --- Enhanced Sidebar Controls ---
with st.sidebar:
    st.markdown("<div class='control-section'>", unsafe_allow_html=True)
    st.markdown("### 🎛️ System Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        # Add inline styling to ensure text visibility
        if st.button("🎯 Smart Assignment", key="smart_assign", help="Intelligently assign tasks to available AGVs"):
            assignments = st.session_state.warehouse.taskassignmentsystem.smarttaskassignment(
                st.session_state.tasks, st.session_state.agvs, st.session_state.log)
            if assignments > 0:
                st.success(f"✅ {assignments} tasks assigned!")
            else:
                st.warning("⚠️ No assignments possible")
        
        # Add custom CSS for this specific button
        st.markdown("""
        <style>
        div[data-testid="column"]:first-child button[kind="primary"] {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            border: 2px solid #059669 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚨 Emergency Recovery", key="emergency", help="Manually recover failed AGVs"):
            recovered = 0
            for agv in st.session_state.agvs:
                if agv.failed and agv.faultseverity >= 2:
                    agv.manualrecover(st.session_state.log)
                    recovered += 1
            if recovered > 0:
                st.success(f"🔧 {recovered} AGVs recovered!")
        
        # Add custom CSS for this specific button
        st.markdown("""
        <style>
        div[data-testid="column"]:last-child button[kind="primary"] {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            border: 2px solid #dc2626 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 Recover Lost Tasks", key="recover", help="Reassign tasks from recovered AGVs"):
        recovered = st.session_state.warehouse.taskassignmentsystem.recoverlosttasks(
            st.session_state.agvs, st.session_state.log)
        if recovered > 0:
            st.success(f"📋 {recovered} tasks recovered!")
    
    # Custom styling for recover button
    st.markdown("""
    <style>
    button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: 2px solid #1d4ed8 !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Auto-run controls
    st.markdown("<div class='control-section'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Simulation")
    st.session_state.autorun = st.toggle("🔄 Auto Simulation", value=st.session_state.autorun, 
                                        help="Automatically run simulation steps")
    
    simulation_speed = st.slider("Simulation Speed", 0.5, 5.0, 2.0, 0.5, 
                               help="Control simulation update frequency")
    
    if st.button("▶️ Manual Step", key="manual_step", help="Run one simulation step"):
        # Simulation step logic
        for agv in st.session_state.agvs:
            agv.inducefault(st.session_state.log, st.session_state.tasks)
            agv.autorecover(st.session_state.log)
            completed_task = agv.move()
            if completed_task:
                st.session_state.completedtasks.append(completed_task)
                st.session_state.log.append(f"✅ Task T-{completed_task.id} completed by AGV-{agv.id:03d}")
        
        st.session_state.warehouse.taskassignmentsystem.smarttaskassignment(
            st.session_state.tasks, st.session_state.agvs, st.session_state.log)
        st.session_state.stepcount += 1
        
        kpis = st.session_state.warehouse.calculatekpis(st.session_state.agvs, st.session_state.tasks)
        kpis['step'] = st.session_state.stepcount
        st.session_state.kpihistory.append(kpis)
        
        st.rerun()
    
    # Force button text visibility with JavaScript
    st.markdown("""
    <style>
    /* Additional force styling for all buttons */
    .stButton button,
    button {
        color: white !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
    }
    
    /* Manual step button specific styling */
    button[key="manual_step"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        width: 100% !important;
    }
    </style>
    
    <script>
    // Force text visibility with JavaScript
    setTimeout(function() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.style.color = 'white';
            button.style.fontWeight = '600';
            button.style.textShadow = 'none';
        });
        
        const labels = document.querySelectorAll('label');
        labels.forEach(label => {
            label.style.color = '#374151';
            label.style.fontWeight = '500';
        });
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # System Status
    st.markdown("<div class='control-section'>", unsafe_allow_html=True)
    st.markdown("### 📊 Quick Status")
    
    if st.session_state.kpihistory:
        latest_kpi = st.session_state.kpihistory[-1]
        availability = latest_kpi['availability']
        
        if availability >= 90:
            status_color = "#10b981"
            status_text = "Excellent"
        elif availability >= 70:
            status_color = "#f59e0b"
            status_text = "Good"
        else:
            status_color = "#ef4444"
            status_text = "Critical"
        
        st.markdown(f"""
            <div style="text-align: center; padding: 16px; background: white; border-radius: 12px; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <div style="font-size: 24px; font-weight: bold; color: {status_color};">{availability:.1f}%</div>
                <div style="color: #64748b;">Fleet Availability</div>
                <div style="margin-top: 8px; padding: 4px 12px; background: {status_color}20; 
                           color: {status_color}; border-radius: 20px; font-weight: 600; font-size: 12px;">
                    {status_text.upper()}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Auto-run logic
# Auto-run logic
if st.session_state.autorun:
    time.sleep(1.0 / simulation_speed)
    
    # Run simulation step
    for agv in st.session_state.agvs:
        # FIX: Pass 4 arguments to enable the Takeover feature
        agv.inducefault(
            st.session_state.log, 
            st.session_state.tasks, 
            st.session_state.agvs, 
            st.session_state.warehouse.taskassignmentsystem
        )
        
        agv.autorecover(st.session_state.log)
        completed_task = agv.move()
        
        if completed_task:
            st.session_state.completedtasks.append(completed_task)
            st.session_state.log.append(f"✅ Task T-{completed_task.id} completed by AGV-{agv.id:03d}")
    
    # Run the regular smart assignment for unassigned tasks
    st.session_state.warehouse.taskassignmentsystem.smarttaskassignment(
        st.session_state.tasks, st.session_state.agvs, st.session_state.log)
    
    st.session_state.stepcount += 1
    
    # KPI Updates
    kpis = st.session_state.warehouse.calculatekpis(st.session_state.agvs, st.session_state.tasks)
    kpis['step'] = st.session_state.stepcount
    st.session_state.kpihistory.append(kpis)
    
    st.rerun()

# KPI calculations
if st.session_state.kpihistory:
    latest_kpi = st.session_state.kpihistory[-1]
    availability = latest_kpi['availability']
    reassignment_rate = latest_kpi['reassignmentrate']
    
    # System status alerts
    if availability >= 90:
        st.markdown(f"""
            <div class="status-card success-alert">
                <strong>🟢 System Status: Excellent</strong><br>
                Fleet Availability: {availability:.1f}% • All systems operational
            </div>
        """, unsafe_allow_html=True)
    elif availability >= 70:
        st.markdown(f"""
            <div class="status-card warning-alert">
                <strong>🟡 System Status: Good</strong><br>
                Fleet Availability: {availability:.1f}% • Some units may need attention
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="status-card critical-alert pulse-animation">
                <strong>🔴 System Status: Critical</strong><br>
                Fleet Availability: {availability:.1f}% • Immediate action required
            </div>
        """, unsafe_allow_html=True)
    
    if reassignment_rate > 0:
        st.markdown(f"""
            <div class="status-card info-alert">
                <strong>🔄 Active Task Reassignments</strong><br>
                Reassignment Rate: {reassignment_rate:.1f}% • System adapting to failures
            </div>
        """, unsafe_allow_html=True)

# --- Enhanced Tab Structure ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🤖 Fleet Status", "🗺️ Live Map", "🔄 Job Recovery", "📈 Analytics"])

with tab1:
    st.markdown("### 📊 Real-time Performance Dashboard")
    
    # KPI Metrics
    if st.session_state.kpihistory:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            delta_avail = latest_kpi['availability'] - st.session_state.kpihistory[-2]['availability'] if len(st.session_state.kpihistory) > 1 else 0
            col1.metric("🎯 Fleet Availability", f"{latest_kpi['availability']:.1f}%", 
                       delta=f"{delta_avail:.1f}%", delta_color="normal")
        
        with col2:
            delta_battery = latest_kpi['avgbattery'] - st.session_state.kpihistory[-2]['avgbattery'] if len(st.session_state.kpihistory) > 1 else 0
            col2.metric("🔋 Avg Battery", f"{latest_kpi['avgbattery']:.1f}%", 
                       delta=f"{delta_battery:.1f}%", delta_color="normal")
        
        with col3:
            delta_network = latest_kpi['networkhealth'] - st.session_state.kpihistory[-2]['networkhealth'] if len(st.session_state.kpihistory) > 1 else 0
            col3.metric("🌐 Network Health", f"{latest_kpi['networkhealth']:.0f}%", 
                       delta=f"{delta_network:.1f}%", delta_color="normal")
        
        with col4:
            delta_pending = latest_kpi['pendingtasks'] - st.session_state.kpihistory[-2]['pendingtasks'] if len(st.session_state.kpihistory) > 1 else 0
            col4.metric("📋 Pending Tasks", latest_kpi['pendingtasks'], 
                       delta=int(delta_pending), delta_color="inverse")
        
        with col5:
            delta_reassign = latest_kpi['reassignmentrate'] - st.session_state.kpihistory[-2]['reassignmentrate'] if len(st.session_state.kpihistory) > 1 else 0
            col5.metric("🔄 Reassignment Rate", f"{latest_kpi['reassignmentrate']:.1f}%", 
                       delta=f"{delta_reassign:.1f}%", delta_color="inverse")
    
    # Performance Charts
    if len(st.session_state.kpihistory) > 1:
        st.markdown("### 📈 Performance Trends")
        
        df_kpi = pd.DataFrame(st.session_state.kpihistory)
        
        # Create enhanced dashboard charts
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                "🎯 Fleet Availability (%)", "🔄 Task Reassignment Rate (%)", "⚡ Task Efficiency (%)",
                "🌐 Network Health (%)", "🔋 Average Battery Level (%)", "📊 System Load"
            ),
            specs=[[{}, {}, {}], [{}, {}, {}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.08
        )
        
        # Fleet Availability
        fig.add_trace(go.Scatter(
            x=df_kpi['step'], y=df_kpi['availability'],
            mode="lines+markers", name="Availability",
            line=dict(color='#10b981', width=3),
            marker=dict(size=8, color='#10b981'),
            fill='tonexty', fillcolor='rgba(16, 185, 129, 0.1)'
        ), row=1, col=1)
        
        # Reassignment Rate
        fig.add_trace(go.Scatter(
            x=df_kpi['step'], y=df_kpi['reassignmentrate'],
            mode="lines+markers", name="Reassignments",
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=8, color='#f59e0b')
        ), row=1, col=2)
        
        # Task Efficiency
        fig.add_trace(go.Scatter(
            x=df_kpi['step'], y=df_kpi['efficiency'],
            mode="lines+markers", name="Efficiency",
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8, color='#3b82f6'),
            fill='tonexty', fillcolor='rgba(59, 130, 246, 0.1)'
        ), row=2, col=1)
        
        # Network Health
        fig.add_trace(go.Scatter(
            x=df_kpi['step'], y=df_kpi['networkhealth'],
            mode="lines+markers", name="Network",
            line=dict(color='#8b5cf6', width=3),
            marker=dict(size=8, color='#8b5cf6')
        ), row=2, col=2)
        
        # Battery Level
        fig.add_trace(go.Scatter(
            x=df_kpi['step'], y=df_kpi['avgbattery'],
            mode="lines+markers", name="Battery",
            line=dict(color='#06b6d4', width=3),
            marker=dict(size=8, color='#06b6d4'),
            fill='tonexty', fillcolor='rgba(6, 182, 212, 0.1)'
        ), row=2, col=3)
        
        # System Load (Pending Tasks)
        fig.add_trace(go.Bar(
            x=df_kpi['step'], y=df_kpi['pendingtasks'],
            name="Pending Tasks",
            marker=dict(color='#ef4444', opacity=0.7)
        ), row=1, col=3)
        
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text="🚀 Real-time System Performance Analytics",
            title_x=0.5,
            title_font=dict(size=20, color='#1e293b'),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Update all subplot axes
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        
        st.plotly_chart(fig, use_container_width=True)
    
    # System Health Indicators
    st.markdown("### 🏥 System Health Indicators")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        failed_agvs = sum(1 for agv in st.session_state.agvs if agv.failed)
        total_agvs = len(st.session_state.agvs)
        health_score = ((total_agvs - failed_agvs) / total_agvs) * 100
        
        if health_score >= 90:
            health_class = "perf-excellent"
            health_icon = "🟢"
        elif health_score >= 70:
            health_class = "perf-good" 
            health_icon = "🟡"
        elif health_score >= 50:
            health_class = "perf-warning"
            health_icon = "🟠"
        else:
            health_class = "perf-critical"
            health_icon = "🔴"
            
        st.markdown(f"""
            <div class="performance-indicator {health_class}">
                {health_icon} <strong>Overall Health:</strong> {health_score:.1f}%
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_battery = sum(agv.batterylevel for agv in st.session_state.agvs) / len(st.session_state.agvs)
        if avg_battery >= 70:
            battery_class = "perf-excellent"
            battery_icon = "🔋"
        elif avg_battery >= 40:
            battery_class = "perf-good"
            battery_icon = "🔋"
        elif avg_battery >= 20:
            battery_class = "perf-warning"
            battery_icon = "🪫"
        else:
            battery_class = "perf-critical"
            battery_icon = "🪫"
            
        st.markdown(f"""
            <div class="performance-indicator {battery_class}">
                {battery_icon} <strong>Battery Status:</strong> {avg_battery:.1f}%
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        active_tasks = sum(1 for agv in st.session_state.agvs if agv.task)
        utilization = (active_tasks / len(st.session_state.agvs)) * 100
        
        if utilization >= 80:
            util_class = "perf-excellent"
            util_icon = "📈"
        elif utilization >= 60:
            util_class = "perf-good"
            util_icon = "📊"
        elif utilization >= 30:
            util_class = "perf-warning"
            util_icon = "📉"
        else:
            util_class = "perf-critical"
            util_icon = "📉"
            
        st.markdown(f"""
            <div class="performance-indicator {util_class}">
                {util_icon} <strong>Utilization:</strong> {utilization:.1f}%
            </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 🤖 Fleet Status & Health Monitoring")
    
    # Fleet summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    available_agvs = sum(1 for agv in st.session_state.agvs if not agv.failed and not agv.task)
    working_agvs = sum(1 for agv in st.session_state.agvs if agv.task and not agv.failed)
    failed_agvs = sum(1 for agv in st.session_state.agvs if agv.failed)
    charging_agvs = sum(1 for agv in st.session_state.agvs if agv.batterylevel < 30 and not agv.failed)
    
    col1.metric("🟢 Available", available_agvs)
    col2.metric("🔵 Working", working_agvs)
    col3.metric("🔴 Failed", failed_agvs)
    col4.metric("🟡 Low Battery", charging_agvs)
    
    # Detailed fleet table
    fleet_data = []
    for agv in st.session_state.agvs:
        health_score = agv.gethealthscore()
        current_task = f"T-{agv.task.id}" if agv.task else "None"
        
        if agv.failed:
            status = "Failed"
            status_class = "status-failed"
        elif agv.task:
            status = "Working"
            status_class = "status-working"
        elif agv.batterylevel < 30:
            status = "Charging"
            status_class = "status-charging"
        else:
            status = "Available"
            status_class = "status-available"
        
        fleet_data.append({
            "AGV ID": f"AGV-{agv.id:03d}",
            "Position": f"({agv.x}, {agv.y})",
            "Status": status,
            "Status_Class": status_class,
            "Current Task": current_task,
            "Fault Type": agv.faulttype or "None",
            "Severity": f"Level {agv.faultseverity}" if agv.failed else "N/A",
            "Battery": f"{agv.batterylevel:.1f}%",
            "Health Score": f"{health_score:.1f}",
            "Tasks Completed": agv.taskcompletioncount,
            "Distance Traveled": f"{agv.totaldistance}m"
        })
    
    # Create interactive fleet status cards
    for i, data in enumerate(fleet_data):
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
            
            with col1:
                st.markdown(f"""
                    <div class="fleet-card">
                        <h4 style="margin: 0; color: #1e293b;">{data['AGV ID']}</h4>
                        <p style="margin: 5px 0; color: #64748b;">Position: {data['Position']}</p>
                        <span class="status-badge {data['Status_Class']}">{data['Status']}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                battery_color = "#ef4444" if float(data['Battery'].replace('%', '')) < 30 else "#10b981"
                st.markdown(f"""
                    <div class="fleet-card">
                        <div style="color: {battery_color}; font-size: 24px; font-weight: bold; margin-bottom: 5px;">
                            🔋 {data['Battery']}
                        </div>
                        <p style="margin: 0; color: #64748b; font-size: 12px;">Battery Level</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                health_color = "#10b981" if float(data['Health Score']) >= 80 else "#f59e0b" if float(data['Health Score']) >= 60 else "#ef4444"
                st.markdown(f"""
                    <div class="fleet-card">
                        <div style="color: {health_color}; font-size: 24px; font-weight: bold; margin-bottom: 5px;">
                            ❤️ {data['Health Score']}
                        </div>
                        <p style="margin: 0; color: #64748b; font-size: 12px;">Health Score</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if data['Status'] == "Failed":
                    st.markdown(f"**Error:** {data['Fault Type']}")
        # Check if this AGV is currently a 'hero' interceptor
                elif agv.intercept_info: 
                    st.markdown(f"<span style='color: #f97316; font-weight: bold;'>⚠️ {agv.intercept_info}</span>", unsafe_allow_html=True)
                else:
                    st.write(f"Task: {data['Current Task']}")
                    
                    # markdown(f"<span style = 'color: #f97316; font-weight: bold;'>⚠️ {agv.intercept_info}</span>", unsafe_allow_html=True")
                # else:
                    
                # st.markdown(f"""
                #     <div class="fleet-card">
                #         <div style="display: flex; justify-content: space-between; align-items: center;">
                #             <div>
                #                 <strong>Current Task:</strong> {data['Current Task']}<br>
                #                 <strong>Fault:</strong> {data['Fault Type']}<br>
                #                 <strong>Completed:</strong> {data['Tasks Completed']} tasks
                #             </div>
                #             <div style="text-align: right; color: #64748b;">
                #                 <div>{data['Distance Traveled']}</div>
                #                 <div style="font-size: 12px;">Total Distance</div>
                #             </div>
                #         </div>
                #     </div>
                # """, unsafe_allow_html=True)

with tab3:
    st.markdown("### 🗺️ Live Digital Twin & Traffic Control")
    
    # Advanced Map controls
    col1, col2, col3 = st.columns(3)
    show_paths = col1.toggle("Show Movement Trails", value=True)
    show_intentions = col2.toggle("Show Intention Lines", value=True)
    theme = col3.selectbox("Map Theme", ["Cyber Night", "Blueprint Mode"])
    
    st.markdown("<div class='map-container' style='background: #0f172a; padding: 10px;'>", unsafe_allow_html=True)
    
    fig = go.Figure()
    
    # Theme settings
    is_dark = theme == "Cyber Night"
    bg_color = '#020617' if is_dark else '#f8fafc'
    grid_color = '#1e293b' if is_dark else '#e2e8f0'
    text_color = '#94a3b8' if is_dark else '#475569'

    # 1. NEW: Danger Zones (Radial ripples around failed AGVs)
    for agv in st.session_state.agvs:
        if agv.failed:
            # Draw a subtle pulsing danger radius around the breakdown
            fig.add_shape(
                type="circle",
                x0=agv.x - 2, y0=agv.y - 2, x1=agv.x + 2, y1=agv.y + 2,
                fillcolor="rgba(239, 68, 68, 0.1)", line_color="rgba(239, 68, 68, 0.5)",
                line_dash="dot", layer="below"
            )

    # 2. Advanced Movement Trails (Fading Tail)
    if show_paths:
        for agv in st.session_state.agvs:
            if len(agv.path_history) > 1 and not agv.failed:
                hx = [p[0] for p in agv.path_history]
                hy = [p[1] for p in agv.path_history]
                trail_color = '#3b82f6' if agv.task else '#10b981'
                
                # We draw the line twice to create a "Neon Glow" effect
                fig.add_trace(go.Scatter(
                    x=hx, y=hy, mode='lines',
                    line=dict(color=f'rgba(59, 130, 246, 0.1)', width=8), # Glow
                    hoverinfo='skip', showlegend=False
                ))
                fig.add_trace(go.Scatter(
                    x=hx, y=hy, mode='lines',
                    line=dict(color=trail_color, width=2), # Core line
                    hoverinfo='skip', showlegend=False
                ))

    # 3. High-Tech Intention & Takeover Paths
    if show_intentions:
        for agv in st.session_state.agvs:
            if agv.task and not agv.failed:
                if hasattr(agv, 'intercept_info') and agv.intercept_info:
                    # GLOWING TAKEOVER PATH
                    # Base wide transparent line (glow)
                    fig.add_trace(go.Scatter(
                        x=[agv.x, agv.task.x], y=[agv.y, agv.task.y], mode='lines',
                        line=dict(color='rgba(249, 115, 22, 0.2)', width=8), showlegend=False
                    ))
                    # Core dashed line
                    fig.add_trace(go.Scatter(
                        x=[agv.x, agv.task.x], y=[agv.y, agv.task.y], mode='lines',
                        line=dict(color='#f97316', width=3, dash='dash'), name="Takeover", showlegend=False
                    ))
                    # Targeting Reticle at the destination
                    fig.add_trace(go.Scatter(
                        x=[agv.task.x], y=[agv.task.y], mode='markers',
                        marker=dict(symbol='cross-thin-open', size=30, color='#f97316', line_width=2),
                        showlegend=False, hoverinfo='skip'
                    ))
                else:
                    # Standard working intention path (subtle)
                    fig.add_trace(go.Scatter(
                        x=[agv.x, agv.task.x], y=[agv.y, agv.task.y], mode='lines',
                        line=dict(color='rgba(59, 130, 246, 0.3)', width=1, dash='dot'), showlegend=False
                    ))

    # 4. Tasks (Rendered as Supply Crates)
    for task in st.session_state.tasks:
        if task.completed: continue
        
        is_abandoned = any(a.failed and a.losttask and a.losttask.id == task.id for a in st.session_state.agvs)
        color = '#ef4444' if is_abandoned else '#10b981' if task.priority == 1 else '#f59e0b'
        
        # Outer ring for abandoned tasks (No hover)
        if is_abandoned:
            fig.add_trace(go.Scatter(
                x=[task.x], y=[task.y], mode="markers",
                marker=dict(symbol='circle-open', size=25, color='#ef4444', line_width=3),
                showlegend=False, hoverinfo='skip'
            ))

        # Core Task Marker (Notice text is wrapped in brackets [])
        fig.add_trace(go.Scatter(
            x=[task.x], y=[task.y], mode="markers",
            marker=dict(symbol='square', size=14, color=color, line=dict(width=1, color=bg_color)),
            text=[f"📦 <b>Task T-{task.id}</b><br>Priority: {task.priority}"], 
            hovertemplate='%{text}<extra></extra>', showlegend=False
        ))

   # 5. AGVs (Grouped for optimal rendering and perfect hover detection)
    agv_groups = {
        'Idle': {'x': [], 'y': [], 'text': [], 'core': '#10b981', 'ring': 'rgba(16, 185, 129, 0.4)', 'symbol': 'circle'},
        'Working': {'x': [], 'y': [], 'text': [], 'core': '#3b82f6', 'ring': 'rgba(59, 130, 246, 0.4)', 'symbol': 'triangle-up'},
        'Intercepting': {'x': [], 'y': [], 'text': [], 'core': '#f97316', 'ring': 'rgba(249, 115, 22, 0.4)', 'symbol': 'triangle-up'},
        'Low Battery': {'x': [], 'y': [], 'text': [], 'core': '#f59e0b', 'ring': 'rgba(245, 158, 11, 0.4)', 'symbol': 'circle'},
        'Failed': {'x': [], 'y': [], 'text': [], 'core': '#ef4444', 'ring': 'rgba(239, 68, 68, 0.4)', 'symbol': 'x'}
    }

    # Sort AGVs into their respective status groups
    for agv in st.session_state.agvs:
        if agv.failed:
            status = 'Failed'
        elif hasattr(agv, 'intercept_info') and agv.intercept_info:
            status = 'Intercepting'
        elif agv.task:
            status = 'Working'
        elif agv.batterylevel < 30:
            status = 'Low Battery'
        else:
            status = 'Idle'

        takeover_detail = f"<br><b style='color:orange;'>⚠️ {agv.intercept_info}</b>" if hasattr(agv, 'intercept_info') and agv.intercept_info else ""
        hover_text = f"🤖 <b>AGV-{agv.id:03d}</b><br>🔋 {agv.batterylevel:.1f}%<br>📡 Status: {status}{takeover_detail}"
        
        agv_groups[status]['x'].append(agv.x)
        agv_groups[status]['y'].append(agv.y)
        agv_groups[status]['text'].append(hover_text)

    # Plot each group
    for status, data in agv_groups.items():
        if not data['x']: continue # Skip empty groups
        
        # Draw Outer Radar Rings first (behind the core, skipping hover)
        fig.add_trace(go.Scatter(
            x=data['x'], y=data['y'], mode="markers",
            marker=dict(symbol='circle-open', size=28, color=data['ring'], line_width=2),
            showlegend=False, hoverinfo='skip'
        ))
        
        # Draw Inner Cores (on top, with hover data)
        fig.add_trace(go.Scatter(
            x=data['x'], y=data['y'], mode="markers",
            marker=dict(symbol=data['symbol'], size=14, color=data['core'], line=dict(width=2, color=bg_color)),
            text=data['text'], hovertemplate='%{text}<extra></extra>', name=status
        ))

    # Layout & Radar Grid Styling
    fig.update_layout(
        xaxis=dict(
            range=[-2, st.session_state.GRIDSIZE + 2], 
            showgrid=True, gridwidth=1, gridcolor=grid_color, 
            zeroline=True, zerolinewidth=2, zerolinecolor=grid_color,
            tickmode='linear', dtick=5, showticklabels=False # Hides numbers, keeps grid
        ),
        yaxis=dict(
            range=[-2, st.session_state.GRIDSIZE + 2], 
            showgrid=True, gridwidth=1, gridcolor=grid_color, 
            zeroline=True, zerolinewidth=2, zerolinecolor=grid_color,
            tickmode='linear', dtick=5, showticklabels=False
        ),
        plot_bgcolor=bg_color, paper_bgcolor=bg_color, height=650, margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=text_color), bgcolor='rgba(0,0,0,0)'
        ),
        hoverlabel=dict(bgcolor=bg_color, font_size=14, font_family="Inter")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("### 🔄 Job Recovery & Task Management")
    
    # ==========================================
    # 🆕 NEW: Styled Fault & Takeover History
    # This matches the image you provided
    # ==========================================
    st.markdown("#### 📜 Fault & Takeover History")
    
    # Container for the styled log entries
    with st.container():
        # Display the latest 5-8 entries to keep the UI clean
        # Filtering for entries containing specific keywords
        for entry in reversed(st.session_state.log[-15:]):
            if "⚡ DYNAMIC TAKEOVER" in entry:
                # Orange Highlighted Alert Box
                st.markdown(f"""
                    <div style="padding: 12px; background-color: #fff7ed; border-left: 5px solid #f97316; 
                                color: #000000; margin: 8px 0; border-radius: 4px; font-weight: 600; font-size: 0.95rem;">
                        {entry}
                    </div>
                """, unsafe_allow_html=True)
            elif "🚨" in entry or "FAILED" in entry:
                # Bullet point for failures
                st.markdown(f"• {entry}")
            elif "📋 New Task" in entry:
                # Bullet point for new assignments
                st.markdown(f"• {entry}")

    st.divider() # Separation between history and stats

    # --- Existing Recovery statistics ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_reassignments = sum(task.reassignmentcount for task in st.session_state.tasks)
    active_tasks = sum(1 for agv in st.session_state.agvs if agv.task)
    available_agvs = sum(1 for agv in st.session_state.agvs if not agv.failed and not agv.task)
    failed_with_tasks = sum(1 for agv in st.session_state.agvs if agv.failed and agv.losttask)
    
    col1.metric("🔄 Total Reassignments", total_reassignments)
    col2.metric("⚡ Active Tasks", active_tasks)
    col3.metric("✅ Available AGVs", available_agvs)
    col4.metric("⚠️ Tasks at Risk", failed_with_tasks)
    
    # --- Task assignment visualization ---
    col1, col2 = st.columns(2)
    
    with col1:
        assigned_tasks = sum(1 for task in st.session_state.tasks if task.assignedagvid is not None and not task.completed)
        unassigned_tasks = len([t for t in st.session_state.tasks if not t.completed]) - assigned_tasks
        
        fig_assignment = px.pie(
            values=[assigned_tasks, unassigned_tasks],
            names=["Assigned", "Unassigned"],
            title="📊 Task Assignment Status",
            color_discrete_map={"Assigned": "#10b981", "Unassigned": "#f59e0b"},
            hole=0.4
        )
        fig_assignment.update_traces(textposition='inside', textinfo='percent+label')
        fig_assignment.update_layout(font_size=14, title_font_size=18, showlegend=True)
        st.plotly_chart(fig_assignment, use_container_width=True)
    
    with col2:
        priority_counts = {1: 0, 2: 0, 3: 0}
        for task in st.session_state.tasks:
            if not task.completed:
                priority_counts[task.priority] += 1
        
        fig_priority = px.bar(
            x=list(priority_counts.keys()),
            y=list(priority_counts.values()),
            title="🎯 Task Priority Distribution",
            labels={'x': 'Priority Level', 'y': 'Number of Tasks'},
            color=list(priority_counts.keys()),
            color_discrete_map={1: '#10b981', 2: '#f59e0b', 3: '#ef4444'}
        )
        fig_priority.update_layout(showlegend=False, title_font_size=18, xaxis_title="Priority Level", yaxis_title="Number of Tasks")
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # --- Detailed task recovery information ---
    st.markdown("#### 📋 Task Recovery Details")
    
    recovery_data = []
    for task in st.session_state.tasks:
        if not task.completed:
            time_since_created = int((time.time() - task.createdtime) / 60)
            time_to_deadline = int((task.deadline - time.time()) / 60)
            status = "Assigned" if task.assignedagvid else "Pending"
            urgency = "🔴 Critical" if time_to_deadline < 5 else "🟡 Medium" if time_to_deadline < 15 else "🟢 Low"
            
            recovery_data.append({
                "Task ID": f"T-{task.id}",
                "Priority": f"P{task.priority}",
                "Status": status,
                "Assigned AGV": f"AGV-{task.assignedagvid:03d}" if task.assignedagvid else "None",
                "Reassignments": task.reassignmentcount,
                "Age (min)": time_since_created,
                "Deadline (min)": time_to_deadline,
                "Urgency": urgency,
                "Position": f"({task.x}, {task.y})"
            })
    
    if recovery_data:
        df_recovery = pd.DataFrame(recovery_data)
        def style_urgency(row):
            if "Critical" in str(row['Urgency']): return ['background-color: #fee2e2'] * len(row)
            elif "Medium" in str(row['Urgency']): return ['background-color: #fef3c7'] * len(row)
            else: return ['background-color: #d1fae5'] * len(row)
        
        st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
        st.dataframe(df_recovery.style.apply(style_urgency, axis=1), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
with tab5:
    st.markdown("### 📈 Advanced Analytics & Insights")
    
    if len(st.session_state.kpihistory) > 5:
        # Performance correlation analysis
        df_kpi = pd.DataFrame(st.session_state.kpihistory)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Availability vs Efficiency scatter plot
            fig_corr = px.scatter(
                df_kpi, x='availability', y='efficiency',
                size='avgbattery', color='reassignmentrate',
                title="🔍 Availability vs Efficiency Analysis",
                labels={
                    'availability': 'Fleet Availability (%)',
                    'efficiency': 'Task Efficiency (%)',
                    'avgbattery': 'Avg Battery Level',
                    'reassignmentrate': 'Reassignment Rate (%)'
                },
                hover_data=['step', 'networkhealth', 'pendingtasks']
            )
            fig_corr.update_layout(height=400)
            st.plotly_chart(fig_corr, use_container_width=True)
        
        with col2:
            # System health heatmap
            recent_data = df_kpi.tail(10)
            metrics = ['availability', 'efficiency', 'avgbattery', 'networkhealth']
            heatmap_data = recent_data[metrics].values.T
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=heatmap_data,
                x=recent_data['step'].values,
                y=['Availability', 'Efficiency', 'Avg Battery', 'Network Health'],
                colorscale='RdYlGn',
                text=heatmap_data,
                texttemplate="%{text:.1f}",
                textfont={"size": 10},
                colorbar=dict(title="Performance %")
            ))
            
            fig_heatmap.update_layout(
                title="🌡️ System Health Heatmap",
                height=400,
                xaxis_title="Simulation Step",
                yaxis_title="Metrics"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Predictive insights
        st.markdown("#### 🔮 Predictive Insights")
        
        # Calculate trends
        if len(df_kpi) >= 5:
            recent_availability = df_kpi['availability'].tail(5).mean()
            recent_battery = df_kpi['avgbattery'].tail(5).mean()
            recent_efficiency = df_kpi['efficiency'].tail(5).mean()
            
            insights = []
            
            if recent_availability < 80:
                insights.append("⚠️ Fleet availability trending downward - consider maintenance scheduling")
            
            if recent_battery < 40:
                insights.append("🔋 Battery levels critically low across fleet - implement charging strategy")
            
            if recent_efficiency < 60:
                insights.append("📉 Task efficiency declining - review task assignment algorithms")
            
            if df_kpi['reassignmentrate'].tail(5).mean() > 10:
                insights.append("🔄 High reassignment rate detected - investigate AGV reliability issues")
            
            if not insights:
                insights.append("✅ System operating within normal parameters")
            
            for insight in insights:
                st.info(insight)
    else:
        st.info("📊 Advanced analytics will be available after collecting more performance data. Continue running the simulation to unlock insights!")

# --- Enhanced Event Log ---
with st.expander("📝 System Event Log & Monitoring", expanded=False):
    col1, col2, col3 = st.columns([2, 2, 1])
    
    log_filter = col1.selectbox(
        "🔍 Filter Events",
        ["All", "🚨 Failures", "✅ Recoveries", "📋 Task Events", "🔄 Reassignments"],
        help="Filter log entries by event type"
    )
    
    log_level = col2.selectbox(
        "📊 Log Level",
        ["All", "Critical", "Warning", "Info"],
        help="Filter by log severity level"
    )
    
    max_entries = col3.number_input("Max Entries", 5, 50, 20, help="Number of entries to display")
    
    # Filter log entries
    if log_filter == "🚨 Failures":
        filtered_log = [event for event in st.session_state.log if "FAULT" in event or "🚨" in event]
    elif log_filter == "✅ Recoveries":
        filtered_log = [event for event in st.session_state.log if "RECOVERY" in event or "✅" in event or "🔧" in event]
    elif log_filter == "📋 Task Events":
        filtered_log = [event for event in st.session_state.log if any(keyword in event for keyword in ["completed", "Task T-", "📋"])]
    elif log_filter == "🔄 Reassignments":
        filtered_log = [event for event in st.session_state.log if "REASSIGNMENT" in event or "returned to queue" in event or "🔄" in event]
    else:
        filtered_log = st.session_state.log
    
    # Apply log level filtering
    if log_level == "Critical":
        filtered_log = [event for event in filtered_log if any(indicator in event for indicator in ["🚨", "FAULT", "CRITICAL"])]
    elif log_level == "Warning":
        filtered_log = [event for event in filtered_log if any(indicator in event for indicator in ["⚠️", "WARNING", "🟡"])]
    elif log_level == "Info":
        filtered_log = [event for event in filtered_log if not any(indicator in event for indicator in ["🚨", "⚠️", "FAULT", "WARNING", "CRITICAL"])]
    
    st.markdown(f"<div class='log-container'>", unsafe_allow_html=True)
    st.markdown(f"<strong>📊 Showing {min(len(filtered_log), max_entries)} of {len(filtered_log)} events</strong><br><br>")
    
    for i, event in enumerate(reversed(filtered_log[-max_entries:])):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add color coding based on event type
        if "🚨" in event or "FAULT" in event:
            event_color = "#ef4444"
        elif "✅" in event or "completed" in event:
            event_color = "#10b981"
        elif "⚠️" in event or "🟡" in event:
            event_color = "#f59e0b"
        elif "🔄" in event:
            event_color = "#3b82f6"
        else:
            event_color = "#64748b"
        
        st.markdown(f"""
            <div style="margin: 5px 0; padding: 8px; border-left: 3px solid {event_color}; background: rgba(255,255,255,0.05);">
                <span style="color: #94a3b8;">[{timestamp}]</span> 
                <span style="color: {event_color};">●</span> 
                {event}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- Dynamic Task Generation ---
if len(st.session_state.tasks) - len(st.session_state.completedtasks) < 5 and random.random() < 0.2:
    new_task = Task(
        len(st.session_state.tasks) + len(st.session_state.completedtasks) + 1000,
        random.randint(0, st.session_state.GRIDSIZE),
        random.randint(0, st.session_state.GRIDSIZE),
        priority=random.choice([1, 2, 3]),
        deadline=time.time() + random.randint(300, 1800)
    )
    st.session_state.tasks.append(new_task)
    st.session_state.log.append(f"🆕 New task T-{new_task.id} generated at ({new_task.x},{new_task.y}) with priority {new_task.priority}")

# --- Remove completed tasks from active list ---
st.session_state.tasks = [task for task in st.session_state.tasks if not task.completed]

# --- Footer with system information ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div style="text-align: center; padding: 16px;">
            <h4 style="color: #64748b; margin: 0;">🕒 Simulation Step</h4>
            <div style="font-size: 24px; font-weight: bold; color: #1e293b;">{st.session_state.stepcount}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    total_completed = len(st.session_state.completedtasks)
    st.markdown(f"""
        <div style="text-align: center; padding: 16px;">
            <h4 style="color: #64748b; margin: 0;">✅ Tasks Completed</h4>
            <div style="font-size: 24px; font-weight: bold; color: #10b981;">{total_completed}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    total_distance = sum(agv.totaldistance for agv in st.session_state.agvs)
    st.markdown(f"""
        <div style="text-align: center; padding: 16px;">
            <h4 style="color: #64748b; margin: 0;">🛣️ Total Distance</h4>
            <div style="font-size: 24px; font-weight: bold; color: #3b82f6;">{total_distance}m</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    system_uptime = st.session_state.stepcount * 30  # Assuming 30 seconds per step
    hours = system_uptime // 3600
    minutes = (system_uptime % 3600) // 60
    st.markdown(f"""
        <div style="text-align: center; padding: 16px;">
            <h4 style="color: #64748b; margin: 0;">⏱️ System Uptime</h4>
            <div style="font-size: 24px; font-weight: bold; color: #8b5cf6;">{hours:02d}:{minutes:02d}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Real-time notifications ---
if st.session_state.log:
    recent_events = st.session_state.log[-3:]
    critical_events = [event for event in recent_events if "🚨" in event or "FAULT" in event]
    
    if critical_events:
        for event in critical_events:
            st.error(f"🚨 **CRITICAL ALERT:** {event}")
    
    success_events = [event for event in recent_events if "✅" in event and "completed" in event]
    if success_events and len(success_events) >= 2:
        st.success(f"🎉 **PRODUCTIVITY BOOST:** {len(success_events)} tasks completed recently!")

# Add some final styling and animations
st.markdown("""
<script>
// Add some subtle animations to metrics
document.addEventListener('DOMContentLoaded', function() {
    const metrics = document.querySelectorAll('[data-testid="metric-container"]');
    metrics.forEach((metric, index) => {
        metric.style.animation = `fadeInUp 0.6s ease-out ${index * 0.1}s both`;
    });
});

// CSS for fade in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .metric-container {
        position: relative;
        overflow: hidden;
    }
    
    .metric-container::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.5s ease;
        opacity: 0;
    }
    
    .metric-container:hover::after {
        animation: shine 1s ease-in-out;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); opacity: 0; }
    }
`;
document.head.appendChild(style);
</script>
""", unsafe_allow_html=True)

# Auto-refresh for real-time updates
if st.session_state.autorun:
    time.sleep(0.1)  # Small delay to prevent too rapid updates
    st.rerun()
