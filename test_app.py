import streamlit as st
import requests as req
import random
import pandas as pd
import numpy as np
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="AGV Fleet Management System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================
# 🔐 FIREBASE EMAIL/PASSWORD AUTH
# ======================================
def firebase_login(email, password, action="login"):
    api_key = st.secrets["FIREBASE_KEY"]
    if action == "signup":
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    else:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = req.post(url, json=payload)
    return response.json()

def show_login():
    st.markdown("""
        <div style='text-align:center; margin-top:60px; margin-bottom:30px'>
            <h1>🤖 AGV Fleet Management System</h1>
            <p style='color:#64748b;'>Sign in to access the dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])

        with tab_login:
            email = st.text_input("Email", key="login_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            if st.button("Login", key="login_btn", use_container_width=True):
                if email and password:
                    with st.spinner("Signing in..."):
                        result = firebase_login(email, password, "login")
                    if "idToken" in result:
                        st.session_state.user_email = result["email"]
                        st.session_state.user_token = result["idToken"]
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        error_msg = result.get("error", {}).get("message", "Login failed")
                        if "EMAIL_NOT_FOUND" in error_msg or "INVALID_LOGIN_CREDENTIALS" in error_msg:
                            st.error("❌ Invalid email or password")
                        elif "INVALID_EMAIL" in error_msg:
                            st.error("❌ Invalid email format")
                        else:
                            st.error(f"❌ {error_msg}")
                else:
                    st.warning("⚠️ Please enter email and password")

        with tab_signup:
            new_email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
            new_password = st.text_input("Password", type="password", key="signup_password", placeholder="Min 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            if st.button("Create Account", key="signup_btn", use_container_width=True):
                if new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            result = firebase_login(new_email, new_password, "signup")
                        if "idToken" in result:
                            st.session_state.user_email = result["email"]
                            st.session_state.user_token = result["idToken"]
                            st.session_state.logged_in = True
                            st.rerun()
                        else:
                            error_msg = result.get("error", {}).get("message", "Signup failed")
                            if "EMAIL_EXISTS" in error_msg:
                                st.error("❌ Email already registered. Please login.")
                            elif "WEAK_PASSWORD" in error_msg:
                                st.error("❌ Password too weak. Use at least 6 characters.")
                            else:
                                st.error(f"❌ {error_msg}")
                else:
                    st.warning("⚠️ Please fill all fields")
    st.stop()

# ======================================
# 🚀 RUN LOGIN BEFORE APP LOADS
# ======================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login()


# --- 3D Cartoon Avatar Display ---
user_email = st.session_state.get('user_email', 'User')

st.sidebar.markdown(f"""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 15px;">
        <img src="https://github.com/anu292004/DynamicFaultRecoveryProject/blob/c7ae56933ef2bc020ac94d6744515f6795d96365/avatar.png" 
             style="width: 110px; height: 110px; border-radius: 50%; 
                    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.25); 
                    border: 3px solid #667eea; object-fit: cover; 
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    transition: transform 0.3s ease;">
    </div>
""", unsafe_allow_html=True)

st.sidebar.success(f"👋 {user_email}")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
# st.sidebar.success(f"👋 {st.session_state.get('user_email', 'User')}")
# if st.sidebar.button("🚪 Logout"):
#     for key in list(st.session_state.keys()):
#         del st.session_state[key]
#     st.rerun()

# --- Enhanced Custom CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem; border-radius: 20px; color: white;
        text-align: center; margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .status-card {
        background: white; border-radius: 16px; padding: 20px; margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-left: 4px solid;
        transition: all 0.3s ease;
    }
    .critical-alert { background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%); border-left-color: #dc2626; color: #991b1b; }
    .warning-alert { background: linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%); border-left-color: #d97706; color: #92400e; }
    .success-alert { background: linear-gradient(135deg, #d1fae5 0%, #f0fdf4 100%); border-left-color: #059669; color: #065f46; }
    .info-alert { background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%); border-left-color: #2563eb; color: #1d4ed8; }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; border: none !important; border-radius: 12px !important;
        padding: 0.5rem 1rem !important; font-weight: 600 !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%) !important;
        color: white !important;
    }
    .fleet-card {
        background: white; border-radius: 16px; padding: 16px; margin: 8px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
    }
    .status-badge {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 12px; font-weight: 600; text-transform: uppercase;
    }
    .status-available { background: #d1fae5; color: #065f46; }
    .status-working { background: #dbeafe; color: #1e40af; }
    .status-failed { background: #fee2e2; color: #991b1b; }
    .status-charging { background: #fef3c7; color: #92400e; }
    .pulse-animation { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .7; } }
    .control-section {
        background: white; border-radius: 16px; padding: 20px; margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
    }
    .map-container {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0; padding: 1rem; border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .dataframe-container {
        background: white; border-radius: 16px; overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
    }
    .log-container {
        background: #1e293b; color: #e2e8f0; padding: 20px; border-radius: 12px;
        font-family: 'Monaco', 'Menlo', monospace; font-size: 13px; line-height: 1.5;
        max-height: 400px; overflow-y: auto;
    }
    .performance-indicator {
        display: flex; align-items: center; gap: 8px; padding: 8px 16px;
        border-radius: 8px; font-weight: 500; margin: 4px 0;
    }
    .perf-excellent { background: #d1fae5; color: #065f46; }
    .perf-good { background: #dbeafe; color: #1e40af; }
    .perf-warning { background: #fef3c7; color: #92400e; }
    .perf-critical { background: #fee2e2; color: #991b1b; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; padding: 0px 24px;
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border-radius: 12px; color: #64748b !important; font-weight: 500;
        border: 2px solid #e2e8f0; transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; border-color: transparent;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    .stSidebar > div {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        border-right: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

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
        self.path_history.append((self.x, self.y))
        if len(self.path_history) > 6:
            self.path_history.pop(0)
        if self.x == self.task.x and self.y == self.task.y:
            completed_task = self.task
            self.task = None
            self.taskcompletioncount += 1
            completed_task.completed = True
            self.intercept_info = None
            self.path_history = [(self.x, self.y)]
            return completed_task
        return None

    def inducefault(self, log, tasks, fleet, assignment_system):
        if not self.failed and random.random() < 0.02:
            self.failed = True
            self.faulttype = random.choice(["LiDAR Error", "Battery Crit", "Motor Jam"])
            if self.task:
                self.losttask = self.task
                log.append(f"🚨 AGV-{self.id:03d} FAILED ({self.faulttype}) while on T-{self.losttask.id}")
                assignment_system.trigger_immediate_takeover(self, fleet, log)
                self.task = None
            else:
                log.append(f"🚨 AGV-{self.id:03d} FAILED ({self.faulttype})")

    def autorecover(self, log):
        if self.failed and self.faultseverity <= 2 and random.random() < 0.15:
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
        candidates = [a for a in fleet if not a.failed and not a.task and a.id != failed_agv.id]
        if candidates:
            best_backup = min(candidates, key=lambda a: abs(a.x - failed_agv.x) + abs(a.y - failed_agv.y))
            best_backup.task = failed_agv.losttask
            best_backup.task.assignedagvid = best_backup.id
            best_backup.intercept_info = f"Recovering T-{best_backup.task.id} from failed AGV-{failed_agv.id:03d}"
            log.append(f"⚡ DYNAMIC TAKEOVER: AGV-{best_backup.id:03d} is now doing failed AGV-{failed_agv.id:03d}'s Task T-{best_backup.task.id}")
            failed_agv.losttask = None
            return True
        log.append(f"⚠️ TAKEOVER FAILED: No idle AGVs available to help AGV-{failed_agv.id:03d}")
        return False

    def smarttaskassignment(self, tasks, agvs, log):
        assignments = 0
        unassigned_tasks = [t for t in tasks if not t.assignedagvid and not t.completed]
        available_agvs = [a for a in agvs if not a.failed and not a.task]
        unassigned_tasks.sort(key=lambda t: (t.priority, t.deadline))
        for task in unassigned_tasks:
            if not available_agvs:
                break
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
            'availability': availability, 'avgbattery': avg_battery,
            'reassignmentrate': reassignment_rate, 'efficiency': efficiency,
            'networkhealth': network_health, 'pendingtasks': pending_tasks
        }


# --- System Initialization ---
GRIDSIZE = 25
NUMAGVS = 8
NUMTASKS = 15

if 'agvs' not in st.session_state:
    st.session_state.agvs = [AGV(i, random.randint(0, GRIDSIZE), random.randint(0, GRIDSIZE)) for i in range(NUMAGVS)]
    st.session_state.tasks = [Task(i, random.randint(0, GRIDSIZE), random.randint(0, GRIDSIZE),
                                   random.choice([1, 2, 3]), time.time() + random.randint(300, 1800)) for i in range(NUMTASKS)]
    st.session_state.warehouse = WarehouseSystem()
    st.session_state.log = []
    st.session_state.autorun = False
    st.session_state.GRIDSIZE = GRIDSIZE
    st.session_state.stepcount = 0
    st.session_state.kpihistory = []
    st.session_state.completedtasks = []

# --- Header ---
st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🤖 AGV Fleet Management System</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">Intelligent Autonomous Vehicle Fleet Operations & Real-time Monitoring</p>
    </div>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("<div class='control-section'>", unsafe_allow_html=True)
    st.markdown("### 🎛️ System Controls")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 Smart Assignment", key="smart_assign"):
            assignments = st.session_state.warehouse.taskassignmentsystem.smarttaskassignment(
                st.session_state.tasks, st.session_state.agvs, st.session_state.log)
            if assignments > 0:
                st.success(f"✅ {assignments} tasks assigned!")
            else:
                st.warning("⚠️ No assignments possible")

    with col2:
        if st.button("🚨 Emergency Recovery", key="emergency"):
            recovered = 0
            for agv in st.session_state.agvs:
                if agv.failed and agv.faultseverity >= 2:
                    agv.manualrecover(st.session_state.log)
                    recovered += 1
            if recovered > 0:
                st.success(f"🔧 {recovered} AGVs recovered!")

    if st.button("🔄 Recover Lost Tasks", key="recover"):
        recovered = st.session_state.warehouse.taskassignmentsystem.recoverlosttasks(
            st.session_state.agvs, st.session_state.log)
        if recovered > 0:
            st.success(f"📋 {recovered} tasks recovered!")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='control-section'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Simulation")
    st.session_state.autorun = st.toggle("🔄 Auto Simulation", value=st.session_state.autorun)
    simulation_speed = st.slider("Simulation Speed", 0.5, 5.0, 2.0, 0.5)

    if st.button("▶️ Manual Step", key="manual_step"):
        for agv in st.session_state.agvs:
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
        st.session_state.warehouse.taskassignmentsystem.smarttaskassignment(
            st.session_state.tasks, st.session_state.agvs, st.session_state.log)
        st.session_state.stepcount += 1
        kpis = st.session_state.warehouse.calculatekpis(st.session_state.agvs, st.session_state.tasks)
        kpis['step'] = st.session_state.stepcount
        st.session_state.kpihistory.append(kpis)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='control-section'>", unsafe_allow_html=True)
    st.markdown("### 📊 Quick Status")
    if st.session_state.kpihistory:
        latest_kpi = st.session_state.kpihistory[-1]
        availability = latest_kpi['availability']
        status_color = "#10b981" if availability >= 90 else "#f59e0b" if availability >= 70 else "#ef4444"
        status_text = "Excellent" if availability >= 90 else "Good" if availability >= 70 else "Critical"
        st.markdown(f"""
            <div style="text-align: center; padding: 16px; background: white; border-radius: 12px;">
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
if st.session_state.autorun:
    time.sleep(1.0 / simulation_speed)
    for agv in st.session_state.agvs:
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
    st.session_state.warehouse.taskassignmentsystem.smarttaskassignment(
        st.session_state.tasks, st.session_state.agvs, st.session_state.log)
    st.session_state.stepcount += 1
    kpis = st.session_state.warehouse.calculatekpis(st.session_state.agvs, st.session_state.tasks)
    kpis['step'] = st.session_state.stepcount
    st.session_state.kpihistory.append(kpis)
    st.rerun()

# KPI Status Alerts
if st.session_state.kpihistory:
    latest_kpi = st.session_state.kpihistory[-1]
    availability = latest_kpi['availability']
    reassignment_rate = latest_kpi['reassignmentrate']
    if availability >= 90:
        st.markdown(f'<div class="status-card success-alert"><strong>🟢 System Status: Excellent</strong><br>Fleet Availability: {availability:.1f}%</div>', unsafe_allow_html=True)
    elif availability >= 70:
        st.markdown(f'<div class="status-card warning-alert"><strong>🟡 System Status: Good</strong><br>Fleet Availability: {availability:.1f}%</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-card critical-alert pulse-animation"><strong>🔴 System Status: Critical</strong><br>Fleet Availability: {availability:.1f}%</div>', unsafe_allow_html=True)
    if reassignment_rate > 0:
        st.markdown(f'<div class="status-card info-alert"><strong>🔄 Active Task Reassignments</strong><br>Reassignment Rate: {reassignment_rate:.1f}%</div>', unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🤖 Fleet Status", "🗺️ Live Map", "🔄 Job Recovery", "📈 Analytics"])

with tab1:
    st.markdown("### 📊 Real-time Performance Dashboard")
    if st.session_state.kpihistory:
        latest_kpi = st.session_state.kpihistory[-1]
        col1, col2, col3, col4, col5 = st.columns(5)
        delta_avail = latest_kpi['availability'] - st.session_state.kpihistory[-2]['availability'] if len(st.session_state.kpihistory) > 1 else 0
        col1.metric("🎯 Fleet Availability", f"{latest_kpi['availability']:.1f}%", delta=f"{delta_avail:.1f}%")
        delta_battery = latest_kpi['avgbattery'] - st.session_state.kpihistory[-2]['avgbattery'] if len(st.session_state.kpihistory) > 1 else 0
        col2.metric("🔋 Avg Battery", f"{latest_kpi['avgbattery']:.1f}%", delta=f"{delta_battery:.1f}%")
        delta_network = latest_kpi['networkhealth'] - st.session_state.kpihistory[-2]['networkhealth'] if len(st.session_state.kpihistory) > 1 else 0
        col3.metric("🌐 Network Health", f"{latest_kpi['networkhealth']:.0f}%", delta=f"{delta_network:.1f}%")
        delta_pending = latest_kpi['pendingtasks'] - st.session_state.kpihistory[-2]['pendingtasks'] if len(st.session_state.kpihistory) > 1 else 0
        col4.metric("📋 Pending Tasks", latest_kpi['pendingtasks'], delta=int(delta_pending), delta_color="inverse")
        delta_reassign = latest_kpi['reassignmentrate'] - st.session_state.kpihistory[-2]['reassignmentrate'] if len(st.session_state.kpihistory) > 1 else 0
        col5.metric("🔄 Reassignment Rate", f"{latest_kpi['reassignmentrate']:.1f}%", delta=f"{delta_reassign:.1f}%", delta_color="inverse")

    if len(st.session_state.kpihistory) > 1:
        st.markdown("### 📈 Performance Trends")
        df_kpi = pd.DataFrame(st.session_state.kpihistory)
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=("🎯 Fleet Availability (%)", "🔄 Reassignment Rate (%)", "⚡ Task Efficiency (%)",
                            "🌐 Network Health (%)", "🔋 Avg Battery Level (%)", "📊 System Load"),
            vertical_spacing=0.12, horizontal_spacing=0.08
        )
        fig.add_trace(go.Scatter(x=df_kpi['step'], y=df_kpi['availability'], mode="lines+markers",
            line=dict(color='#10b981', width=3), marker=dict(size=8)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_kpi['step'], y=df_kpi['reassignmentrate'], mode="lines+markers",
            line=dict(color='#f59e0b', width=3), marker=dict(size=8)), row=1, col=2)
        fig.add_trace(go.Scatter(x=df_kpi['step'], y=df_kpi['efficiency'], mode="lines+markers",
            line=dict(color='#3b82f6', width=3), marker=dict(size=8)), row=2, col=1)
        fig.add_trace(go.Scatter(x=df_kpi['step'], y=df_kpi['networkhealth'], mode="lines+markers",
            line=dict(color='#8b5cf6', width=3), marker=dict(size=8)), row=2, col=2)
        fig.add_trace(go.Scatter(x=df_kpi['step'], y=df_kpi['avgbattery'], mode="lines+markers",
            line=dict(color='#06b6d4', width=3), marker=dict(size=8)), row=2, col=3)
        fig.add_trace(go.Bar(x=df_kpi['step'], y=df_kpi['pendingtasks'],
            marker=dict(color='#ef4444', opacity=0.7)), row=1, col=3)
        fig.update_layout(height=600, showlegend=False, plot_bgcolor='white', paper_bgcolor='white')
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏥 System Health Indicators")
    col1, col2, col3 = st.columns(3)
    with col1:
        failed_agvs = sum(1 for agv in st.session_state.agvs if agv.failed)
        total_agvs = len(st.session_state.agvs)
        health_score = ((total_agvs - failed_agvs) / total_agvs) * 100
        hc = "perf-excellent" if health_score >= 90 else "perf-good" if health_score >= 70 else "perf-warning" if health_score >= 50 else "perf-critical"
        hi = "🟢" if health_score >= 90 else "🟡" if health_score >= 70 else "🟠" if health_score >= 50 else "🔴"
        st.markdown(f'<div class="performance-indicator {hc}">{hi} <strong>Overall Health:</strong> {health_score:.1f}%</div>', unsafe_allow_html=True)
    with col2:
        avg_battery = sum(agv.batterylevel for agv in st.session_state.agvs) / len(st.session_state.agvs)
        bc = "perf-excellent" if avg_battery >= 70 else "perf-good" if avg_battery >= 40 else "perf-warning" if avg_battery >= 20 else "perf-critical"
        bi = "🔋" if avg_battery >= 40 else "🪫"
        st.markdown(f'<div class="performance-indicator {bc}">{bi} <strong>Battery Status:</strong> {avg_battery:.1f}%</div>', unsafe_allow_html=True)
    with col3:
        active_tasks = sum(1 for agv in st.session_state.agvs if agv.task)
        utilization = (active_tasks / len(st.session_state.agvs)) * 100
        uc = "perf-excellent" if utilization >= 80 else "perf-good" if utilization >= 60 else "perf-warning" if utilization >= 30 else "perf-critical"
        ui = "📈" if utilization >= 60 else "📉"
        st.markdown(f'<div class="performance-indicator {uc}">{ui} <strong>Utilization:</strong> {utilization:.1f}%</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("### 🤖 Fleet Status & Health Monitoring")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🟢 Available", sum(1 for agv in st.session_state.agvs if not agv.failed and not agv.task))
    col2.metric("🔵 Working", sum(1 for agv in st.session_state.agvs if agv.task and not agv.failed))
    col3.metric("🔴 Failed", sum(1 for agv in st.session_state.agvs if agv.failed))
    col4.metric("🟡 Low Battery", sum(1 for agv in st.session_state.agvs if agv.batterylevel < 30 and not agv.failed))

    for agv in st.session_state.agvs:
        health_score = agv.gethealthscore()
        current_task = f"T-{agv.task.id}" if agv.task else "None"
        if agv.failed:
            status, status_class = "Failed", "status-failed"
        elif agv.task:
            status, status_class = "Working", "status-working"
        elif agv.batterylevel < 30:
            status, status_class = "Charging", "status-charging"
        else:
            status, status_class = "Available", "status-available"

        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
            with col1:
                st.markdown(f"""<div class="fleet-card">
                    <h4 style="margin:0;color:#1e293b;">AGV-{agv.id:03d}</h4>
                    <p style="margin:5px 0;color:#64748b;">Position: ({agv.x}, {agv.y})</p>
                    <span class="status-badge {status_class}">{status}</span>
                </div>""", unsafe_allow_html=True)
            with col2:
                bc = "#ef4444" if agv.batterylevel < 30 else "#10b981"
                st.markdown(f"""<div class="fleet-card">
                    <div style="color:{bc};font-size:24px;font-weight:bold;">🔋 {agv.batterylevel:.1f}%</div>
                    <p style="margin:0;color:#64748b;font-size:12px;">Battery Level</p>
                </div>""", unsafe_allow_html=True)
            with col3:
                hc = "#10b981" if health_score >= 80 else "#f59e0b" if health_score >= 60 else "#ef4444"
                st.markdown(f"""<div class="fleet-card">
                    <div style="color:{hc};font-size:24px;font-weight:bold;">❤️ {health_score:.1f}</div>
                    <p style="margin:0;color:#64748b;font-size:12px;">Health Score</p>
                </div>""", unsafe_allow_html=True)
            with col4:
                if agv.failed:
                    st.markdown(f"**Error:** {agv.faulttype or 'Unknown'}")
                elif agv.intercept_info:
                    st.markdown(f"<span style='color:#f97316;font-weight:bold;'>⚠️ {agv.intercept_info}</span>", unsafe_allow_html=True)
                else:
                    st.write(f"Task: {current_task}")

with tab3:
    st.markdown("### 🗺️ Live Digital Twin & Traffic Control")
    col1, col2, col3 = st.columns(3)
    show_paths = col1.toggle("Show Movement Trails", value=True)
    show_intentions = col2.toggle("Show Intention Lines", value=True)
    theme = col3.selectbox("Map Theme", ["Cyber Night", "Blueprint Mode"])

    fig = go.Figure()
    is_dark = theme == "Cyber Night"
    bg_color = '#020617' if is_dark else '#f8fafc'
    grid_color = '#1e293b' if is_dark else '#e2e8f0'
    text_color = '#94a3b8' if is_dark else '#475569'

    for agv in st.session_state.agvs:
        if agv.failed:
            fig.add_shape(type="circle", x0=agv.x-2, y0=agv.y-2, x1=agv.x+2, y1=agv.y+2,
                fillcolor="rgba(239,68,68,0.1)", line_color="rgba(239,68,68,0.5)", line_dash="dot", layer="below")

    if show_paths:
        for agv in st.session_state.agvs:
            if len(agv.path_history) > 1 and not agv.failed:
                hx = [p[0] for p in agv.path_history]
                hy = [p[1] for p in agv.path_history]
                trail_color = '#3b82f6' if agv.task else '#10b981'
                fig.add_trace(go.Scatter(x=hx, y=hy, mode='lines',
                    line=dict(color='rgba(59,130,246,0.1)', width=8), hoverinfo='skip', showlegend=False))
                fig.add_trace(go.Scatter(x=hx, y=hy, mode='lines',
                    line=dict(color=trail_color, width=2), hoverinfo='skip', showlegend=False))

    if show_intentions:
        for agv in st.session_state.agvs:
            if agv.task and not agv.failed:
                if agv.intercept_info:
                    fig.add_trace(go.Scatter(x=[agv.x, agv.task.x], y=[agv.y, agv.task.y], mode='lines',
                        line=dict(color='rgba(249,115,22,0.2)', width=8), showlegend=False))
                    fig.add_trace(go.Scatter(x=[agv.x, agv.task.x], y=[agv.y, agv.task.y], mode='lines',
                        line=dict(color='#f97316', width=3, dash='dash'), showlegend=False))
                else:
                    fig.add_trace(go.Scatter(x=[agv.x, agv.task.x], y=[agv.y, agv.task.y], mode='lines',
                        line=dict(color='rgba(59,130,246,0.3)', width=1, dash='dot'), showlegend=False))

    for task in st.session_state.tasks:
        if task.completed: continue
        is_abandoned = any(a.failed and a.losttask and a.losttask.id == task.id for a in st.session_state.agvs)
        color = '#ef4444' if is_abandoned else '#10b981' if task.priority == 1 else '#f59e0b'
        fig.add_trace(go.Scatter(x=[task.x], y=[task.y], mode="markers",
            marker=dict(symbol='square', size=14, color=color),
            text=[f"📦 <b>Task T-{task.id}</b><br>Priority: {task.priority}"],
            hovertemplate='%{text}<extra></extra>', showlegend=False))

    agv_groups = {
        'Idle': {'x': [], 'y': [], 'text': [], 'core': '#10b981', 'ring': 'rgba(16,185,129,0.4)', 'symbol': 'circle'},
        'Working': {'x': [], 'y': [], 'text': [], 'core': '#3b82f6', 'ring': 'rgba(59,130,246,0.4)', 'symbol': 'triangle-up'},
        'Intercepting': {'x': [], 'y': [], 'text': [], 'core': '#f97316', 'ring': 'rgba(249,115,22,0.4)', 'symbol': 'triangle-up'},
        'Low Battery': {'x': [], 'y': [], 'text': [], 'core': '#f59e0b', 'ring': 'rgba(245,158,11,0.4)', 'symbol': 'circle'},
        'Failed': {'x': [], 'y': [], 'text': [], 'core': '#ef4444', 'ring': 'rgba(239,68,68,0.4)', 'symbol': 'x'}
    }
    for agv in st.session_state.agvs:
        if agv.failed: s = 'Failed'
        elif agv.intercept_info: s = 'Intercepting'
        elif agv.task: s = 'Working'
        elif agv.batterylevel < 30: s = 'Low Battery'
        else: s = 'Idle'
        td = f"<br><b style='color:orange;'>⚠️ {agv.intercept_info}</b>" if agv.intercept_info else ""
        agv_groups[s]['x'].append(agv.x)
        agv_groups[s]['y'].append(agv.y)
        agv_groups[s]['text'].append(f"🤖 <b>AGV-{agv.id:03d}</b><br>🔋 {agv.batterylevel:.1f}%<br>📡 {s}{td}")

    for status, data in agv_groups.items():
        if not data['x']: continue
        fig.add_trace(go.Scatter(x=data['x'], y=data['y'], mode="markers",
            marker=dict(symbol='circle-open', size=28, color=data['ring'], line_width=2),
            showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=data['x'], y=data['y'], mode="markers",
            marker=dict(symbol=data['symbol'], size=14, color=data['core'], line=dict(width=2, color=bg_color)),
            text=data['text'], hovertemplate='%{text}<extra></extra>', name=status))

    fig.update_layout(
        xaxis=dict(range=[-2, st.session_state.GRIDSIZE+2], showgrid=True, gridwidth=1,
            gridcolor=grid_color, tickmode='linear', dtick=5, showticklabels=False),
        yaxis=dict(range=[-2, st.session_state.GRIDSIZE+2], showgrid=True, gridwidth=1,
            gridcolor=grid_color, tickmode='linear', dtick=5, showticklabels=False),
        plot_bgcolor=bg_color, paper_bgcolor=bg_color, height=650,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=text_color), bgcolor='rgba(0,0,0,0)'),
        hoverlabel=dict(bgcolor=bg_color, font_size=14, font_family="Inter")
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### 🔄 Job Recovery & Task Management")
    st.markdown("#### 📜 Fault & Takeover History")
    for entry in reversed(st.session_state.log[-15:]):
        if "⚡ DYNAMIC TAKEOVER" in entry:
            st.markdown(f"""<div style="padding:12px;background:#fff7ed;border-left:5px solid #f97316;
                color:#000;margin:8px 0;border-radius:4px;font-weight:600;">{entry}</div>""", unsafe_allow_html=True)
        elif "🚨" in entry or "FAILED" in entry:
            st.markdown(f"• {entry}")
        elif "📋 New Task" in entry:
            st.markdown(f"• {entry}")

    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔄 Total Reassignments", sum(task.reassignmentcount for task in st.session_state.tasks))
    col2.metric("⚡ Active Tasks", sum(1 for agv in st.session_state.agvs if agv.task))
    col3.metric("✅ Available AGVs", sum(1 for agv in st.session_state.agvs if not agv.failed and not agv.task))
    col4.metric("⚠️ Tasks at Risk", sum(1 for agv in st.session_state.agvs if agv.failed and agv.losttask))

    col1, col2 = st.columns(2)
    with col1:
        assigned = sum(1 for t in st.session_state.tasks if t.assignedagvid and not t.completed)
        unassigned = len([t for t in st.session_state.tasks if not t.completed]) - assigned
        fig_pie = px.pie(values=[assigned, unassigned], names=["Assigned", "Unassigned"],
            title="📊 Task Assignment Status", color_discrete_map={"Assigned": "#10b981", "Unassigned": "#f59e0b"}, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        pc = {1: 0, 2: 0, 3: 0}
        for t in st.session_state.tasks:
            if not t.completed: pc[t.priority] += 1
        fig_bar = px.bar(x=list(pc.keys()), y=list(pc.values()), title="🎯 Task Priority Distribution",
            labels={'x': 'Priority', 'y': 'Tasks'}, color=list(pc.keys()),
            color_discrete_map={1: '#10b981', 2: '#f59e0b', 3: '#ef4444'})
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### 📋 Task Recovery Details")
    recovery_data = []
    for task in st.session_state.tasks:
        if not task.completed:
            ttd = int((task.deadline - time.time()) / 60)
            recovery_data.append({
                "Task ID": f"T-{task.id}", "Priority": f"P{task.priority}",
                "Status": "Assigned" if task.assignedagvid else "Pending",
                "Assigned AGV": f"AGV-{task.assignedagvid:03d}" if task.assignedagvid else "None",
                "Reassignments": task.reassignmentcount,
                "Age (min)": int((time.time() - task.createdtime) / 60),
                "Deadline (min)": ttd,
                "Urgency": "🔴 Critical" if ttd < 5 else "🟡 Medium" if ttd < 15 else "🟢 Low",
                "Position": f"({task.x}, {task.y})"
            })
    if recovery_data:
        df_r = pd.DataFrame(recovery_data)
        def style_urgency(row):
            if "Critical" in str(row['Urgency']): return ['background-color: #fee2e2'] * len(row)
            elif "Medium" in str(row['Urgency']): return ['background-color: #fef3c7'] * len(row)
            else: return ['background-color: #d1fae5'] * len(row)
        st.dataframe(df_r.style.apply(style_urgency, axis=1), use_container_width=True, hide_index=True)

with tab5:
    st.markdown("### 📈 Advanced Analytics & Insights")
    if len(st.session_state.kpihistory) > 5:
        df_kpi = pd.DataFrame(st.session_state.kpihistory)
        col1, col2 = st.columns(2)
        with col1:
            fig_corr = px.scatter(df_kpi, x='availability', y='efficiency', size='avgbattery',
                color='reassignmentrate', title="🔍 Availability vs Efficiency",
                labels={'availability': 'Fleet Availability (%)', 'efficiency': 'Task Efficiency (%)'})
            fig_corr.update_layout(height=400)
            st.plotly_chart(fig_corr, use_container_width=True)
        with col2:
            recent = df_kpi.tail(10)
            metrics = ['availability', 'efficiency', 'avgbattery', 'networkhealth']
            fig_heat = go.Figure(data=go.Heatmap(
                z=recent[metrics].values.T, x=recent['step'].values,
                y=['Availability', 'Efficiency', 'Avg Battery', 'Network Health'],
                colorscale='RdYlGn', texttemplate="%{z:.1f}", textfont={"size": 10}))
            fig_heat.update_layout(title="🌡️ System Health Heatmap", height=400)
            st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("#### 🔮 Predictive Insights")
        insights = []
        if df_kpi['availability'].tail(5).mean() < 80:
            insights.append("⚠️ Fleet availability trending downward - consider maintenance scheduling")
        if df_kpi['avgbattery'].tail(5).mean() < 40:
            insights.append("🔋 Battery levels critically low - implement charging strategy")
        if df_kpi['efficiency'].tail(5).mean() < 60:
            insights.append("📉 Task efficiency declining - review assignment algorithms")
        if df_kpi['reassignmentrate'].tail(5).mean() > 10:
            insights.append("🔄 High reassignment rate - investigate AGV reliability")
        if not insights:
            insights.append("✅ System operating within normal parameters")
        for insight in insights:
            st.info(insight)
    else:
        st.info("📊 Advanced analytics available after more simulation steps.")

# Event Log
with st.expander("📝 System Event Log", expanded=False):
    col1, col2, col3 = st.columns([2, 2, 1])
    log_filter = col1.selectbox("🔍 Filter", ["All", "🚨 Failures", "✅ Recoveries", "📋 Task Events", "🔄 Reassignments"])
    log_level = col2.selectbox("📊 Log Level", ["All", "Critical", "Warning", "Info"])
    max_entries = col3.number_input("Max Entries", 5, 50, 20)

    if log_filter == "🚨 Failures":
        filtered_log = [e for e in st.session_state.log if "FAULT" in e or "🚨" in e]
    elif log_filter == "✅ Recoveries":
        filtered_log = [e for e in st.session_state.log if "RECOVERY" in e or "✅" in e or "🔧" in e]
    elif log_filter == "📋 Task Events":
        filtered_log = [e for e in st.session_state.log if any(k in e for k in ["completed", "Task T-", "📋"])]
    elif log_filter == "🔄 Reassignments":
        filtered_log = [e for e in st.session_state.log if "REASSIGNMENT" in e or "🔄" in e]
    else:
        filtered_log = st.session_state.log

    if log_level == "Critical":
        filtered_log = [e for e in filtered_log if any(i in e for i in ["🚨", "FAULT", "CRITICAL"])]
    elif log_level == "Warning":
        filtered_log = [e for e in filtered_log if any(i in e for i in ["⚠️", "WARNING"])]
    elif log_level == "Info":
        filtered_log = [e for e in filtered_log if not any(i in e for i in ["🚨", "⚠️", "FAULT"])]

    st.markdown(f"<div class='log-container'><strong>📊 Showing {min(len(filtered_log), max_entries)} of {len(filtered_log)} events</strong><br><br>", unsafe_allow_html=True)
    for event in reversed(filtered_log[-max_entries:]):
        ts = datetime.now().strftime("%H:%M:%S")
        ec = "#ef4444" if "🚨" in event else "#10b981" if "✅" in event else "#f59e0b" if "⚠️" in event else "#3b82f6" if "🔄" in event else "#64748b"
        st.markdown(f"""<div style="margin:5px 0;padding:8px;border-left:3px solid {ec};background:rgba(255,255,255,0.05);">
            <span style="color:#94a3b8;">[{ts}]</span> <span style="color:{ec};">●</span> {event}</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Dynamic Task Generation
if len(st.session_state.tasks) - len(st.session_state.completedtasks) < 5 and random.random() < 0.2:
    new_task = Task(len(st.session_state.tasks) + 1000,
        random.randint(0, st.session_state.GRIDSIZE), random.randint(0, st.session_state.GRIDSIZE),
        priority=random.choice([1, 2, 3]), deadline=time.time() + random.randint(300, 1800))
    st.session_state.tasks.append(new_task)
    st.session_state.log.append(f"🆕 New task T-{new_task.id} generated at ({new_task.x},{new_task.y})")

st.session_state.tasks = [t for t in st.session_state.tasks if not t.completed]

# Footer
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div style="text-align:center;padding:16px;"><h4 style="color:#64748b;margin:0;">🕒 Simulation Step</h4><div style="font-size:24px;font-weight:bold;color:#1e293b;">{st.session_state.stepcount}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div style="text-align:center;padding:16px;"><h4 style="color:#64748b;margin:0;">✅ Tasks Completed</h4><div style="font-size:24px;font-weight:bold;color:#10b981;">{len(st.session_state.completedtasks)}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div style="text-align:center;padding:16px;"><h4 style="color:#64748b;margin:0;">🛣️ Total Distance</h4><div style="font-size:24px;font-weight:bold;color:#3b82f6;">{sum(a.totaldistance for a in st.session_state.agvs)}m</div></div>', unsafe_allow_html=True)
with col4:
    uptime = st.session_state.stepcount * 30
    st.markdown(f'<div style="text-align:center;padding:16px;"><h4 style="color:#64748b;margin:0;">⏱️ System Uptime</h4><div style="font-size:24px;font-weight:bold;color:#8b5cf6;">{uptime//3600:02d}:{(uptime%3600)//60:02d}</div></div>', unsafe_allow_html=True)

# Real-time notifications
if st.session_state.log:
    recent = st.session_state.log[-3:]
    for event in recent:
        if "🚨" in event or "FAULT" in event:
            st.error(f"🚨 **CRITICAL ALERT:** {event}")

if st.session_state.autorun:
    time.sleep(0.1)
    st.rerun()
