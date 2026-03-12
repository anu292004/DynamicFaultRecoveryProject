import streamlit as st
import streamlit.components.v1 as components
import requests as req
import random
import math
import pandas as pd
import json
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --- PAGE CONFIGURATION ---
# Changed layout to "wide" to allow for a split-screen design
st.set_page_config(page_title="AGV Fleet Manager | Login", page_icon="🤖", layout="wide")

# --- CUSTOM CSS ---
def apply_custom_css():
    st.markdown("""
        <style>
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            color: #1E293B;
            margin-bottom: -10px;
        }
        .sub-title {
            color: #64748B;
            font-size: 1.2rem;
            margin-bottom: 20px;
        }
        /* Style the tabs to look modern */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

# --- FIREBASE LOGIC ---
def firebase_login(email, password, action="login"):
    api_key = st.secrets["FIREBASE_KEY"]
    url = (f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
           if action == "signup"
           else f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}")
    return req.post(url, json={"email": email, "password": password, "returnSecureToken": True}).json()

# --- LOGIN UI ---
def show_login():
    apply_custom_css()
    
    # --- SPLIT SCREEN LAYOUT ---
    # col_img for visual objects, col_spacer for breathing room, col_form for the login
    col_img, col_spacer, col_form = st.columns([1.2, 0.1, 1])

  # --- LEFT COLUMN: VISUAL OBJECTS ---
    with col_img:
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.markdown('<p class="main-title">🤖 AGV Fleet Control</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Intelligent warehouse automation at your fingertips.</p>', unsafe_allow_html=True)
        
        # Object 1: A high-quality hero image (Using a placeholder tech/robotics image from Unsplash)
        st.image("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=800&auto=format&fit=crop", 
                 caption="Centralized Robotics Command", use_container_width=True)
        
        st.write("") # Spacer
        
        # Object 2: "Fake" live status widgets to make the UI feel active and industrial
        stat_col1, stat_col2 = st.columns(2)
        stat_col1.info("🟢 **System Status:** Online & Ready")
        stat_col2.success("📦 **Active AGVs:** 42 Deployed")
        
    # --- RIGHT COLUMN: LOGIN FORM ---
    with col_form:
        st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
        
        # Object 3: The Login Card
        with st.container(border=True):
            st.markdown("### Welcome Back 👋")
            st.write("Please sign in to continue to your dashboard.")
            st.divider() # Object 4: Clean visual separator
            
            tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])
            
            # --- LOGIN TAB ---
            with tab_login:
                email    = st.text_input("Email",    key="login_email",    placeholder="admin@fleet.com")
                password = st.text_input("Password", key="login_password", placeholder="••••••••", type="password")
                st.write("") 
                
                if st.button("Access Dashboard", key="login_btn", type="primary", use_container_width=True):
                    if email and password:
                        with st.spinner("Authenticating..."):
                            result = firebase_login(email, password, "login")
                        if "idToken" in result:
                            st.session_state.update(user_email=result["email"],
                                                    user_token=result["idToken"], 
                                                    logged_in=True)
                            st.rerun()
                        else:
                            msg = result.get("error", {}).get("message", "Login failed")
                            st.error("❌ Invalid email or password" if "INVALID" in msg else f"❌ {msg}")
                    else:
                        st.warning("⚠️ Please enter both email and password")
                        
            # --- SIGNUP TAB ---
            with tab_signup:
                ne  = st.text_input("Email",            key="signup_email",    placeholder="newuser@fleet.com")
                np_ = st.text_input("Password",         key="signup_password", placeholder="Min 6 characters", type="password")
                cp  = st.text_input("Confirm Password", key="confirm_password", placeholder="••••••••", type="password")
                st.write("") 
                
                if st.button("Create Account", key="signup_btn", type="primary", use_container_width=True):
                    if ne and np_ and cp:
                        if np_ != cp:       
                            st.error("❌ Passwords do not match")
                        elif len(np_) < 6:  
                            st.error("❌ Password must be at least 6 characters")
                        else:
                            with st.spinner("Provisioning account..."):
                                result = firebase_login(ne, np_, "signup")
                            if "idToken" in result:
                                st.session_state.update(user_email=result["email"],
                                                        user_token=result["idToken"], 
                                                        logged_in=True)
                                st.rerun()
                            else:
                                msg = result.get("error", {}).get("message", "Signup failed")
                                st.error("❌ Email already registered." if "EMAIL_EXISTS" in msg else f"❌ {msg}")
                    else:
                        st.warning("⚠️ Please fill all fields")
                        
    st.stop()

# --- SESSION STATE MANAGEMENT ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login()
# ======================================
# 🎨 CSS
# ======================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main-header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:2rem;border-radius:20px;
  color:white;text-align:center;margin-bottom:2rem;box-shadow:0 10px 30px rgba(102,126,234,.3);}
.status-card{background:white;border-radius:16px;padding:20px;margin:10px 0;
  box-shadow:0 4px 20px rgba(0,0,0,.08);border-left:4px solid;}
.critical-alert{background:linear-gradient(135deg,#fee2e2,#fef2f2);border-left-color:#dc2626;color:#991b1b;}
.warning-alert {background:linear-gradient(135deg,#fef3c7,#fffbeb);border-left-color:#d97706;color:#92400e;}
.success-alert {background:linear-gradient(135deg,#d1fae5,#f0fdf4);border-left-color:#059669;color:#065f46;}
.stButton>button{background:linear-gradient(135deg,#667eea,#764ba2)!important;color:white!important;
  border:none!important;border-radius:12px!important;padding:.5rem 1rem!important;font-weight:600!important;}
.fleet-card{background:white;border-radius:16px;padding:16px;margin:8px 0;
  box-shadow:0 2px 10px rgba(0,0,0,.05);border:1px solid #e2e8f0;}
.status-badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;text-transform:uppercase;}
.status-available{background:#d1fae5;color:#065f46;} .status-working{background:#dbeafe;color:#1e40af;}
.status-failed{background:#fee2e2;color:#991b1b;}    .status-charging{background:#fef3c7;color:#92400e;}
.control-section{background:white;border-radius:16px;padding:20px;margin:15px 0;
  box-shadow:0 4px 15px rgba(0,0,0,.05);border:1px solid #e2e8f0;}
div[data-testid="metric-container"]{background:linear-gradient(145deg,#fff,#f8fafc);
  border:1px solid #e2e8f0;padding:1rem;border-radius:16px;box-shadow:0 4px 15px rgba(0,0,0,.05);}
.log-container{background:#1e293b;color:#e2e8f0;padding:20px;border-radius:12px;
  font-family:'Monaco',monospace;font-size:13px;line-height:1.5;max-height:400px;overflow-y:auto;}
.perf-indicator{display:flex;align-items:center;gap:8px;padding:8px 16px;border-radius:8px;font-weight:500;margin:4px 0;}
.perf-excellent{background:#d1fae5;color:#065f46;} .perf-good{background:#dbeafe;color:#1e40af;}
.perf-warning{background:#fef3c7;color:#92400e;}   .perf-critical{background:#fee2e2;color:#991b1b;}
.stTabs [data-baseweb="tab-list"]{gap:8px;background:transparent;}
.stTabs [data-baseweb="tab"]{height:50px;padding:0 24px;
  background:linear-gradient(135deg,#f8fafc,#fff);border-radius:12px;
  color:#64748b!important;font-weight:500;border:2px solid #e2e8f0;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#667eea,#764ba2)!important;
  color:white!important;border-color:transparent;box-shadow:0 6px 20px rgba(102,126,234,.4);}
.stSidebar>div{background:linear-gradient(180deg,#f8fafc,#fff);border-right:1px solid #e2e8f0;}
iframe{border:none!important;border-radius:16px;}
</style>
""", unsafe_allow_html=True)

# ======================================
# 🤖 PYTHON SIMULATION ENGINE
# ======================================
GRID      = 25
NUM_AGVS  = 10
NUM_TASKS = 18
STEP_SIZE = 0.5   # units per step
FAULT_PROB = 0.03
RECOVERY_STEPS = (60, 120)

def make_agv(i):
    return {
        "id": i,
        "x": round(random.uniform(1, GRID-1), 2),
        "y": round(random.uniform(1, GRID-1), 2),
        "battery": round(random.uniform(65, 100), 1),
        "failed": False,
        "fault_type": None,
        "intercept": None,
        "task_id": None,
        "recovery_timer": 0,
        "tasks_done": 0,
        "status": "idle",
    }

def make_task(i):
    return {
        "id": i,
        "x": round(random.uniform(1, GRID-1), 2),
        "y": round(random.uniform(1, GRID-1), 2),
        "priority": random.choice([1, 1, 2, 2, 3]),
        "assigned_to": None,
        "completed": False,
    }

def dist(ax, ay, bx, by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def init_fleet():
    st.session_state.agvs           = [make_agv(i) for i in range(NUM_AGVS)]
    st.session_state.tasks          = [make_task(i) for i in range(NUM_TASKS)]
    st.session_state.completed_count = 0
    st.session_state.step_count      = 0
    st.session_state.event_log       = []
    st.session_state.kpi_history     = []
    st.session_state.task_id_counter = NUM_TASKS
    st.session_state.sim_running     = True

def add_log(msg, typ="assign"):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.event_log.insert(0, {"msg": msg, "type": typ, "ts": ts})
    if len(st.session_state.event_log) > 300:
        st.session_state.event_log = st.session_state.event_log[:300]

def assign_tasks():
    agvs  = st.session_state.agvs
    tasks = st.session_state.tasks
    free  = [t for t in tasks if not t["assigned_to"] and not t["completed"]]
    idle  = [a for a in agvs if not a["failed"] and a["task_id"] is None]
    free.sort(key=lambda t: t["priority"])
    for t in free:
        if not idle:
            break
        best = min(idle, key=lambda a: dist(a["x"], a["y"], t["x"], t["y"]))
        t["assigned_to"] = best["id"]
        best["task_id"]  = t["id"]
        best["status"]   = "working"
        idle.remove(best)
        add_log(f"T-{t['id']} → AGV-{best['id']:03d}", "assign")

def do_takeover(failed_agv, lost_task):
    agvs = st.session_state.agvs
    cands = [a for a in agvs if not a["failed"] and a["task_id"] is None and a["id"] != failed_agv["id"]]
    if not cands:
        add_log(f"⚠️ No idle AGV for T-{lost_task['id']}", "fault")
        return
    best = min(cands, key=lambda a: dist(a["x"], a["y"], lost_task["x"], lost_task["y"]))
    lost_task["assigned_to"] = best["id"]
    best["task_id"]   = lost_task["id"]
    best["intercept"] = f"Takeover T-{lost_task['id']}←{failed_agv['id']}"
    best["status"]    = "intercepting"
    add_log(f"⚡ TAKEOVER: AGV-{best['id']:03d} → T-{lost_task['id']}", "takeover")

def trigger_fault(agv):
    if agv["failed"]:
        return
    fault_types = ["LiDAR Error", "Motor Jam", "Battery Crit", "Comm Loss"]
    agv["failed"]     = True
    agv["fault_type"] = random.choice(fault_types)
    agv["status"]     = "failed"
    agv["recovery_timer"] = random.randint(*RECOVERY_STEPS)
    add_log(f"🚨 AGV-{agv['id']:03d} FAULT: {agv['fault_type']}", "fault")
    # Find and free the task
    if agv["task_id"] is not None:
        lost = next((t for t in st.session_state.tasks if t["id"] == agv["task_id"]), None)
        agv["task_id"] = None
        if lost:
            lost["assigned_to"] = None
            do_takeover(agv, lost)

def sim_step():
    """Run one simulation step — called by Python, not JS."""
    agvs  = st.session_state.agvs
    tasks = st.session_state.tasks

    st.session_state.step_count += 1

    # Random faults
    for a in agvs:
        if not a["failed"] and random.random() < FAULT_PROB:
            trigger_fault(a)

    # Recovery
    for a in agvs:
        if a["failed"]:
            a["recovery_timer"] -= 1
            if a["recovery_timer"] <= 0:
                a["failed"]     = False
                a["fault_type"] = None
                a["intercept"]  = None
                a["status"]     = "idle"
                add_log(f"✅ AGV-{a['id']:03d} recovered", "recover")

    # Movement
    for a in agvs:
        if a["failed"] or a["task_id"] is None:
            continue
        task = next((t for t in tasks if t["id"] == a["task_id"]), None)
        if not task:
            a["task_id"] = None
            a["status"]  = "idle"
            continue

        dx = task["x"] - a["x"]
        dy = task["y"] - a["y"]
        d  = math.sqrt(dx*dx + dy*dy)

        if d < STEP_SIZE:
            # Task complete
            a["x"] = task["x"]
            a["y"] = task["y"]
            task["completed"] = True
            st.session_state.completed_count += 1
            a["task_id"]   = None
            a["intercept"] = None
            a["status"]    = "idle"
            a["tasks_done"] += 1
            add_log(f"✅ T-{task['id']} done by AGV-{a['id']:03d}", "complete")
        else:
            a["x"] = round(a["x"] + dx / d * STEP_SIZE, 2)
            a["y"] = round(a["y"] + dy / d * STEP_SIZE, 2)
            a["battery"] = round(max(0, a["battery"] - 0.05), 1)

    # Recharge idle
    for a in agvs:
        if not a["failed"] and a["task_id"] is None:
            a["battery"] = round(min(100, a["battery"] + 0.3), 1)
            a["status"]  = "charging" if a["battery"] < 95 else "idle"

    # Remove completed tasks, spawn new ones
    st.session_state.tasks = [t for t in tasks if not t["completed"]]
    while len(st.session_state.tasks) < NUM_TASKS:
        tid = st.session_state.task_id_counter
        st.session_state.task_id_counter += 1
        nt = make_task(tid)
        st.session_state.tasks.append(nt)
        add_log(f"🆕 T-{tid} spawned", "assign")

    # Re-assign
    assign_tasks()

    # KPI snapshot
    n    = len(agvs) or 1
    ok   = sum(1 for a in agvs if not a["failed"])
    act  = sum(1 for a in agvs if a["task_id"] is not None and not a["failed"])
    done = st.session_state.completed_count
    tt   = len(st.session_state.tasks) + done or 1

    st.session_state.kpi_history.append({
        "step":         st.session_state.step_count,
        "availability": round(ok / n * 100, 1),
        "avgbattery":   round(sum(a["battery"] for a in agvs) / n, 1),
        "utilization":  round(act / n * 100, 1),
        "efficiency":   round(done / tt * 100, 1),
        "pendingtasks": sum(1 for t in st.session_state.tasks if not t["assigned_to"]),
        "networkhealth":round(ok / n * 100, 1),
    })
    if len(st.session_state.kpi_history) > 500:
        st.session_state.kpi_history = st.session_state.kpi_history[-500:]

# ── Init on first load ──────────────────────────────────────────
if "agvs" not in st.session_state:
    init_fleet()
    assign_tasks()

# ======================================
# 🗺️ MAP HTML (pure visualization — reads Python state)
# ======================================
def build_map_html(agvs, tasks, grid=25):
    agv_json  = json.dumps(agvs)
    task_json = json.dumps(tasks)
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#020c18;--dim:#1a3a52;--accent:#00d4ff;--green:#00ff9d;
       --orange:#ff7b00;--red:#ff2d55;--text:#7ec8e3}}
html,body{{width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--text);font-family:'Rajdhani',sans-serif}}
#wrap{{display:flex;flex-direction:column;height:100vh}}
header{{display:flex;align-items:center;justify-content:space-between;
  padding:7px 14px;border-bottom:1px solid var(--dim);background:rgba(0,15,30,.97);flex-shrink:0}}
.brand{{font-family:'Share Tech Mono',monospace;font-size:13px;color:var(--accent);letter-spacing:3px}}
.brand em{{color:var(--green);font-style:normal}}
.hstats{{display:flex;gap:14px}}
.stat{{text-align:center}}
.sv{{font-size:18px;font-weight:700;color:var(--accent);font-family:'Share Tech Mono',monospace;line-height:1}}
.sv.r{{color:var(--red)}} .sv.g{{color:var(--green)}} .sv.o{{color:var(--orange)}}
.sl{{font-size:8px;letter-spacing:2px;text-transform:uppercase;color:#3a6a8a;margin-top:1px}}
.main{{display:flex;flex:1;overflow:hidden}}
#cvw{{flex:1;position:relative;overflow:hidden}}
canvas{{display:block;width:100%;height:100%}}
.sb{{width:210px;flex-shrink:0;background:rgba(0,10,22,.97);
  border-left:1px solid var(--dim);display:flex;flex-direction:column;overflow:hidden}}
.ss{{padding:8px 10px;border-bottom:1px solid var(--dim)}}
.st{{font-size:8px;letter-spacing:3px;text-transform:uppercase;color:#3a6a8a;margin-bottom:6px}}
.al{{overflow-y:auto;padding:4px}}
.al::-webkit-scrollbar{{width:3px}}
.al::-webkit-scrollbar-thumb{{background:var(--dim);border-radius:2px}}
.ac{{background:rgba(0,20,40,.8);border:1px solid var(--dim);border-radius:3px;padding:6px;margin-bottom:4px}}
.ac.working{{border-color:rgba(0,212,255,.4)}}
.ac.failed{{border-color:rgba(255,45,85,.6);background:rgba(40,5,15,.8)}}
.ac.intercepting{{border-color:rgba(255,123,0,.6)}}
.ac.charging{{border-color:rgba(255,215,0,.4)}}
.ar{{display:flex;justify-content:space-between;align-items:center;margin-bottom:3px}}
.ai{{font-family:'Share Tech Mono',monospace;font-size:11px;color:var(--accent)}}
.dot{{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:3px}}
.bb{{height:3px;background:var(--dim);border-radius:2px;overflow:hidden;margin-top:3px}}
.bf{{height:100%;border-radius:2px}}
.an{{font-size:9px;color:#3a6a8a;margin-top:2px}}
.an.hl{{color:var(--orange);font-weight:700}}
.lp{{height:0;overflow:hidden}}
.legend{{display:flex;flex-wrap:wrap;gap:5px}}
.li{{display:flex;align-items:center;gap:3px;font-size:9px;color:#5a8aa5}}
.ld{{width:8px;height:8px;border-radius:50%}} .ls{{width:8px;height:8px;border-radius:2px}}
.tt{{position:absolute;background:rgba(0,10,22,.97);border:1px solid var(--accent);
  color:var(--text);padding:6px 9px;font-size:10px;pointer-events:none;
  border-radius:3px;display:none;white-space:nowrap;z-index:100;font-family:'Share Tech Mono',monospace}}
.pulse-badge{{position:absolute;top:6px;right:6px;font-family:'Share Tech Mono',monospace;
  font-size:8px;color:var(--green);background:rgba(0,255,157,.08);
  border:1px solid rgba(0,255,157,.4);padding:2px 7px;border-radius:3px;letter-spacing:1px;
  animation:blink 2s infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
</style></head><body>
<div id="wrap">
  <header>
    <div class="brand">AGV <em>LIVE</em> <span style="color:#2a4a6a;font-size:9px;margin-left:4px">▸ PYTHON SIMULATION</span></div>
    <div class="hstats">
      <div class="stat"><div class="sv g" id="s0">0</div><div class="sl">Active</div></div>
      <div class="stat"><div class="sv r" id="s1">0</div><div class="sl">Failed</div></div>
      <div class="stat"><div class="sv o" id="s2">0</div><div class="sl">Intercept</div></div>
      <div class="stat"><div class="sv"   id="s3">0</div><div class="sl">Tasks</div></div>
      <div class="stat"><div class="sv g" id="s4">0</div><div class="sl">Done</div></div>
      <div class="stat"><div class="sv"   id="s5">0</div><div class="sl">Step</div></div>
    </div>
  </header>
  <div class="main">
    <div id="cvw">
      <canvas id="map"></canvas>
      <div class="tt" id="tt"></div>
      <div class="pulse-badge">🐍 PYTHON DRIVEN</div>
    </div>
    <div class="sb">
      <div class="ss"><div class="st">Fleet</div>
        <div class="al" id="al" style="max-height:310px"></div>
      </div>
      <div class="ss"><div class="st">Legend</div>
        <div class="legend">
          <div class="li"><div class="ld" style="background:#00ff9d"></div>Idle</div>
          <div class="li"><div class="ld" style="background:#00d4ff"></div>Work</div>
          <div class="li"><div class="ld" style="background:#ff7b00"></div>ICP</div>
          <div class="li"><div class="ld" style="background:#ff2d55"></div>Fail</div>
          <div class="li"><div class="ld" style="background:#ffd700"></div>Charge</div>
          <div class="li"><div class="ls" style="background:#00ff9d"></div>P1</div>
          <div class="li"><div class="ls" style="background:#ffd700"></div>P2</div>
          <div class="li"><div class="ls" style="background:#ff2d55"></div>P3</div>
        </div>
      </div>
    </div>
  </div>
</div>
<script>
// State is injected fresh from Python on every Streamlit rerun
const AGVS  = {agv_json};
const TASKS = {task_json};
const GRID  = {grid};

// Build smooth-interpolation state for 60fps rendering
// Python gives us the target positions; we glide there visually
const vis = AGVS.map(a => ({{
  ...a,
  vx: a.x, vy: a.y,   // visual position (interpolated)
  tx: a.x, ty: a.y,   // target (Python's position)
  trail: [],
}}));

const taskMap = {{}};
TASKS.forEach(t => taskMap[t.id] = t);

const canvas = document.getElementById('map');
const ctx    = canvas.getContext('2d');
let cw, ch, cW, cH, px0, py0, lastTime = 0;

function resize() {{
  const el = document.getElementById('cvw');
  cw = canvas.width  = el.clientWidth;
  ch = canvas.height = el.clientHeight;
  const sz = Math.min(cw, ch) * .92;
  cW = sz / GRID; cH = sz / GRID;
  px0 = (cw - sz) / 2; py0 = (ch - sz) / 2;
}}
const gx = v => px0 + v * cW;
const gy = v => py0 + v * cH;
const dist = (a,b) => Math.sqrt((a.vx-b.x)**2+(a.vy-b.y)**2);

function drawGrid() {{
  ctx.strokeStyle='rgba(10,31,53,0.8)'; ctx.lineWidth=0.5;
  for(let i=0;i<=GRID;i++) {{
    ctx.beginPath();ctx.moveTo(gx(i),gy(0));ctx.lineTo(gx(i),gy(GRID));ctx.stroke();
    ctx.beginPath();ctx.moveTo(gx(0),gy(i));ctx.lineTo(gx(GRID),gy(i));ctx.stroke();
  }}
  ctx.strokeStyle='rgba(0,212,255,0.04)'; ctx.lineWidth=0.4;
  for(let i=5;i<GRID;i+=5) {{
    ctx.beginPath();ctx.moveTo(gx(i),gy(0));ctx.lineTo(gx(i),gy(GRID));ctx.stroke();
    ctx.beginPath();ctx.moveTo(gx(0),gy(i));ctx.lineTo(gx(GRID),gy(i));ctx.stroke();
  }}
}}

function drawTasks() {{
  const PC={{1:'#00ff9d',2:'#ffd700',3:'#ff2d55'}};
  for(const t of TASKS) {{
    const x=gx(t.x),y=gy(t.y),c=PC[t.priority]||'#00d4ff';
    const p=0.5+0.5*Math.sin(Date.now()*.003+t.id);
    const s=cW*.55;
    ctx.shadowBlur=8+p*6; ctx.shadowColor=c;
    ctx.fillStyle=c; ctx.globalAlpha=.15+p*.05;
    ctx.fillRect(x-s/2,y-s/2,s,s); ctx.globalAlpha=1; ctx.shadowBlur=0;
    ctx.strokeStyle=c; ctx.lineWidth=1.5; ctx.globalAlpha=.8;
    ctx.strokeRect(x-s/2,y-s/2,s,s); ctx.globalAlpha=1;
    ctx.fillStyle=c; ctx.font=`bold ${{cW*.35}}px Rajdhani`;
    ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(`P${{t.priority}}`,x,y);
    ctx.fillStyle='rgba(255,255,255,0.3)'; ctx.font=`${{cW*.2}}px Share Tech Mono`;
    ctx.fillText(`T${{t.id}}`,x,y+s/2+8);
  }}
}}

function drawTrails() {{
  for(const a of vis) {{
    if(a.failed||a.trail.length<2) continue;
    const c=a.intercept?'#ff7b00':'#00d4ff';
    for(let i=1;i<a.trail.length;i++) {{
      ctx.strokeStyle=c; ctx.globalAlpha=(i/a.trail.length)*.4; ctx.lineWidth=1.5;
      ctx.beginPath();
      ctx.moveTo(gx(a.trail[i-1].x),gy(a.trail[i-1].y));
      ctx.lineTo(gx(a.trail[i].x),  gy(a.trail[i].y)); ctx.stroke();
    }}
    ctx.globalAlpha=1;
  }}
}}

function drawLines() {{
  for(const a of vis) {{
    if(!a.task_id||a.failed) continue;
    const t=taskMap[a.task_id]; if(!t) continue;
    const ax=gx(a.vx),ay=gy(a.vy),bx=gx(t.x),by=gy(t.y);
    const c=a.intercept?'#ff7b00':'rgba(0,212,255,0.25)';
    ctx.strokeStyle=c; ctx.setLineDash([4,6]); ctx.lineWidth=a.intercept?1.5:1; ctx.globalAlpha=.6;
    ctx.beginPath(); ctx.moveTo(ax,ay); ctx.lineTo(bx,by); ctx.stroke();
    ctx.setLineDash([]); ctx.globalAlpha=1;
    const ang=Math.atan2(by-ay,bx-ax),mx=(ax+bx)/2,my=(ay+by)/2;
    ctx.fillStyle=c; ctx.globalAlpha=.7; ctx.save();
    ctx.translate(mx,my); ctx.rotate(ang);
    ctx.beginPath(); ctx.moveTo(5,0); ctx.lineTo(-4,4); ctx.lineTo(-4,-4);
    ctx.closePath(); ctx.fill(); ctx.restore(); ctx.globalAlpha=1;
  }}
}}

function drawAGVs() {{
  const R=cW*.55;
  for(const a of vis) {{
    const x=gx(a.vx),y=gy(a.vy);
    let c,ring;
    const st=a.status||'idle';
    if(st==='failed')       {{c='#ff2d55';ring='rgba(255,45,85,0.3)';}}
    else if(st==='intercepting'){{c='#ff7b00';ring='rgba(255,123,0,0.3)';}}
    else if(st==='working') {{c='#00d4ff';ring='rgba(0,212,255,0.2)';}}
    else if(st==='charging'){{c='#ffd700';ring='rgba(255,215,0,0.2)';}}
    else                    {{c='#00ff9d';ring='rgba(0,255,157,0.15)';}}
    const p=0.5+0.5*Math.sin(Date.now()*.004+a.id*.7);
    ctx.beginPath(); ctx.arc(x,y,R*(1.4+p*.3),0,Math.PI*2); ctx.fillStyle=ring; ctx.fill();
    ctx.shadowBlur=st==='failed'?20:12; ctx.shadowColor=c;
    ctx.beginPath(); ctx.arc(x,y,R,0,Math.PI*2); ctx.fillStyle=c+'22'; ctx.fill();
    ctx.strokeStyle=c; ctx.lineWidth=2; ctx.stroke(); ctx.shadowBlur=0;
    ctx.beginPath(); ctx.arc(x,y,R*.35,0,Math.PI*2); ctx.fillStyle=c; ctx.fill();
    ctx.fillStyle=st==='failed'?'#ff2d55':'#fff';
    ctx.font=`bold ${{R*.65}}px Rajdhani`; ctx.textAlign='center'; ctx.textBaseline='middle';
    ctx.fillText(a.id,x,y);
    // Battery bar
    const bw=R*1.8;
    ctx.fillStyle='#0a1f35'; ctx.fillRect(x-bw/2,y+R+3,bw,3);
    const bc=a.battery>50?'#00ff9d':a.battery>20?'#ffd700':'#ff2d55';
    ctx.fillStyle=bc; ctx.fillRect(x-bw/2,y+R+3,bw*(a.battery/100),3);
    if(st==='failed') {{
      ctx.strokeStyle='#ff2d55'; ctx.lineWidth=2; const q=R*.5;
      ctx.beginPath(); ctx.moveTo(x-q,y-q); ctx.lineTo(x+q,y+q); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x+q,y-q); ctx.lineTo(x-q,y+q); ctx.stroke();
    }}
    if(a.intercept) {{
      ctx.fillStyle='#ff7b00'; ctx.font=`${{R*.7}}px Rajdhani`;
      ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText('⚡',x+R+4,y-R);
    }}
  }}
}}

function updateSidebar() {{
  document.getElementById('s0').textContent = vis.filter(a=>a.status==='working'||a.status==='intercepting').length;
  document.getElementById('s1').textContent = vis.filter(a=>a.failed).length;
  document.getElementById('s2').textContent = vis.filter(a=>a.status==='intercepting').length;
  document.getElementById('s3').textContent = TASKS.length;
  document.getElementById('s4').textContent = {st.session_state.completed_count};
  document.getElementById('s5').textContent = {st.session_state.step_count};

  document.getElementById('al').innerHTML = vis.map(a => {{
    const st=a.status||'idle';
    let cls='ac',dot='#00ff9d',lbl='IDLE';
    if(st==='failed')       {{cls+=' failed';dot='#ff2d55';lbl='FAIL';}}
    else if(st==='intercepting'){{cls+=' intercepting';dot='#ff7b00';lbl='ICP';}}
    else if(st==='working') {{cls+=' working';dot='#00d4ff';lbl='WORK';}}
    else if(st==='charging'){{cls+=' charging';dot='#ffd700';lbl='CHG';}}
    const bc=a.battery>50?'#00ff9d':a.battery>20?'#ffd700':'#ff2d55';
    const info=a.failed
      ?`<div class="an" style="color:#ff2d55">⚠️${{a.fault_type||''}}</div>`
      :a.intercept?`<div class="an hl">⚡${{a.intercept}}</div>`
      :a.task_id!=null?`<div class="an">→ T-${{a.task_id}} (${{a.vx.toFixed(1)}},${{a.vy.toFixed(1)}})</div>`
      :`<div class="an">Done: ${{a.tasks_done}}</div>`;
    return `<div class="${{cls}}"><div class="ar">
      <span class="ai"><span class="dot" style="background:${{dot}}"></span>AGV-${{String(a.id).padStart(3,'0')}}</span>
      <span style="font-size:8px;color:${{dot}}">${{lbl}}</span></div>
      <div class="bb"><div class="bf" style="width:${{a.battery}}%;background:${{bc}}"></div></div>
      <div class="ar" style="margin-top:2px">
        <span style="font-size:8px;color:#3a6a8a">🔋${{a.battery.toFixed(0)}}%</span>
        <span style="font-size:8px;color:#3a6a8a">(${{a.vx.toFixed(0)}},${{a.vy.toFixed(0)}})</span>
      </div>${{info}}</div>`;
  }}).join('');
}}

function frame(ts) {{
  const dt = Math.min(ts - lastTime, 100) / 1000;
  lastTime = ts;

  // Smooth interpolation toward Python target positions
  for(const a of vis) {{
    const speed = 4.0;
    a.vx += (a.tx - a.vx) * Math.min(1, speed * dt);
    a.vy += (a.ty - a.vy) * Math.min(1, speed * dt);
    a.trail.push({{x:a.vx, y:a.vy}});
    if(a.trail.length > 30) a.trail.shift();
  }}

  ctx.clearRect(0,0,cw,ch);
  const g=ctx.createRadialGradient(cw/2,ch/2,0,cw/2,ch/2,Math.max(cw,ch)/2);
  g.addColorStop(0,'#020c18'); g.addColorStop(1,'#010810');
  ctx.fillStyle=g; ctx.fillRect(0,0,cw,ch);
  drawGrid(); drawTrails(); drawLines(); drawTasks(); drawAGVs();
  requestAnimationFrame(frame);
}}

// Tooltip
canvas.addEventListener('mousemove', e => {{
  const r=canvas.getBoundingClientRect();
  const wx=((e.clientX-r.left)*(cw/r.width)-px0)/cW;
  const wy=((e.clientY-r.top)*(ch/r.height)-py0)/cH;
  const tt=document.getElementById('tt');
  let f=null;
  for(const a of vis) if(Math.sqrt((a.vx-wx)**2+(a.vy-wy)**2)<1.2) {{f={{t:'a',d:a}};break;}}
  if(!f) for(const t of TASKS) if(Math.sqrt((t.x-wx)**2+(t.y-wy)**2)<0.8) {{f={{t:'t',d:t}};break;}}
  if(f) {{
    const d=f.d;
    tt.innerHTML=f.t==='a'
      ?`AGV-${{String(d.id).padStart(3,'0')}}<br>🔋${{d.battery.toFixed(1)}}%<br>${{d.status||'idle'}}<br>Done:${{d.tasks_done}}`
      :`T-${{d.id}} P${{d.priority}}<br>${{d.assigned_to!=null?'AGV-'+String(d.assigned_to).padStart(3,'0'):'Unassigned'}}`;
    tt.style.cssText=`display:block;left:${{e.clientX+14}}px;top:${{e.clientY-8}}px`;
  }} else tt.style.display='none';
}});
canvas.addEventListener('mouseleave',()=>document.getElementById('tt').style.display='none');

window.addEventListener('resize', resize);
resize();
updateSidebar();
requestAnimationFrame(frame);
</script></body></html>"""

# ======================================
# 🖥️ HEADER
# ======================================
st.markdown("""
<div class="main-header">
  <h1 style="margin:0;font-size:2.5rem;font-weight:700;">🤖 AGV Fleet Management System</h1>
  <p style="margin:10px 0 0 0;font-size:1.1rem;opacity:.9;">
    Python Simulation Engine → Live Canvas Visualization
  </p>
</div>
""", unsafe_allow_html=True)

# ======================================
# 🗃️ SIDEBAR
# ======================================
with st.sidebar:
    user_email = st.session_state.get('user_email', 'User')
    st.markdown(f"""
        <div style="text-align:center;margin-top:15px;margin-bottom:15px;">
          <img src="https://cdn-icons-png.flaticon.com/512/8345/8345328.png"
               style="width:110px;height:110px;border-radius:50%;
                      box-shadow:0 8px 20px rgba(102,126,234,.25);
                      border:3px solid #667eea;object-fit:cover;">
        </div>""", unsafe_allow_html=True)
    st.success(f"👋 {user_email}")
    if st.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

    st.markdown("<div class='control-section'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Simulation Controls")

    sim_running = st.toggle("▶ Auto-simulate", value=st.session_state.get("sim_running", True), key="sim_toggle")
    st.session_state.sim_running = sim_running

    speed = st.slider("Steps per cycle", 1, 10, 3, key="sim_speed")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Force Fault", use_container_width=True):
            alive = [a for a in st.session_state.agvs if not a["failed"]]
            if alive:
                trigger_fault(random.choice(alive))
            st.rerun()
    with col2:
        if st.button("🔄 Reset All", use_container_width=True):
            init_fleet()
            assign_tasks()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='control-section'>", unsafe_allow_html=True)
    st.markdown("### 📊 Live Fleet Status")
    agvs_now = st.session_state.agvs
    c1, c2 = st.columns(2)
    c1.metric("🟢 Active",    sum(1 for a in agvs_now if a["task_id"] is not None and not a["failed"]))
    c2.metric("🔴 Failed",    sum(1 for a in agvs_now if a["failed"]))
    c1.metric("⚡ Intercept", sum(1 for a in agvs_now if a.get("intercept") and not a["failed"]))
    c2.metric("✅ Done",      st.session_state.completed_count)

    if st.session_state.kpi_history:
        lk = st.session_state.kpi_history[-1]
        av = lk["availability"]
        color = "#10b981" if av>=90 else "#f59e0b" if av>=70 else "#ef4444"
        label = "Excellent" if av>=90 else "Good" if av>=70 else "Critical"
        st.markdown(f"""
        <div style="text-align:center;padding:14px;background:white;border-radius:12px;margin-top:10px;">
          <div style="font-size:24px;font-weight:bold;color:{color};">{av:.1f}%</div>
          <div style="color:#64748b;">Fleet Availability</div>
          <div style="margin-top:6px;padding:3px 10px;background:{color}20;
               color:{color};border-radius:20px;font-weight:600;font-size:12px;">{label.upper()}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Run simulation steps BEFORE rendering ──
if st.session_state.sim_running:
    for _ in range(speed):
        sim_step()

# KPI banner
if st.session_state.kpi_history:
    lk = st.session_state.kpi_history[-1]
    av = lk["availability"]
    if av >= 90:
        st.markdown(f'<div class="status-card success-alert"><strong>🟢 Excellent</strong> · Availability {av:.1f}% · Step {lk["step"]}</div>', unsafe_allow_html=True)
    elif av >= 70:
        st.markdown(f'<div class="status-card warning-alert"><strong>🟡 Good</strong> · Availability {av:.1f}% · Step {lk["step"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-card critical-alert"><strong>🔴 Critical</strong> · Availability {av:.1f}% · Step {lk["step"]}</div>', unsafe_allow_html=True)

# ======================================
# 📑 TABS
# ======================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Dashboard", "🤖 Fleet Status", "🗺️ Live Map", "📜 Event Log", "📈 Analytics"])

with tab1:
    st.markdown("### 📊 Real-time Performance Dashboard")
    kh = st.session_state.kpi_history
    if kh:
        lk=kh[-1]; pk=kh[-2] if len(kh)>1 else lk
        c1,c2,c3,c4,c5=st.columns(5)
        c1.metric("🎯 Availability", f"{lk['availability']:.1f}%",  f"{lk['availability']-pk['availability']:.1f}%")
        c2.metric("🔋 Avg Battery",  f"{lk['avgbattery']:.1f}%",   f"{lk['avgbattery']-pk['avgbattery']:.1f}%")
        c3.metric("🌐 Network",      f"{lk['networkhealth']:.0f}%", f"{lk['networkhealth']-pk['networkhealth']:.1f}%")
        c4.metric("📋 Pending",      lk['pendingtasks'],            int(lk['pendingtasks']-pk['pendingtasks']), delta_color="inverse")
        c5.metric("⚡ Utilization",  f"{lk['utilization']:.1f}%",  f"{lk['utilization']-pk['utilization']:.1f}%")

    if len(kh) > 2:
        st.markdown("### 📈 Performance Trends")
        df = pd.DataFrame(kh)
        fig = make_subplots(rows=2, cols=3,
            subplot_titles=("🎯 Availability","⚡ Utilization","✅ Efficiency",
                            "🌐 Network","🔋 Battery","📋 Pending"),
            vertical_spacing=0.12, horizontal_spacing=0.08)
        kw = dict(mode="lines+markers", marker=dict(size=5))
        fig.add_trace(go.Scatter(x=df.step, y=df.availability,  line=dict(color='#10b981',width=2),**kw),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.step, y=df.utilization,   line=dict(color='#f59e0b',width=2),**kw),row=1,col=2)
        fig.add_trace(go.Scatter(x=df.step, y=df.efficiency,    line=dict(color='#3b82f6',width=2),**kw),row=2,col=1)
        fig.add_trace(go.Scatter(x=df.step, y=df.networkhealth, line=dict(color='#8b5cf6',width=2),**kw),row=2,col=2)
        fig.add_trace(go.Scatter(x=df.step, y=df.avgbattery,    line=dict(color='#06b6d4',width=2),**kw),row=2,col=3)
        fig.add_trace(go.Bar(x=df.step, y=df.pendingtasks, marker=dict(color='#ef4444',opacity=0.7)),row=1,col=3)
        fig.update_layout(height=550, showlegend=False, plot_bgcolor='white', paper_bgcolor='white')
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏥 System Health")
    c1,c2,c3 = st.columns(3)
    an = st.session_state.agvs
    with c1:
        ok=sum(1 for a in an if not a["failed"]); hs=ok/len(an)*100 if an else 0
        cl="perf-excellent" if hs>=90 else "perf-good" if hs>=70 else "perf-warning" if hs>=50 else "perf-critical"
        ic="🟢" if hs>=90 else "🟡" if hs>=70 else "🟠" if hs>=50 else "🔴"
        st.markdown(f'<div class="perf-indicator {cl}">{ic} <strong>Health:</strong> {hs:.1f}%</div>',unsafe_allow_html=True)
    with c2:
        ab=sum(a["battery"] for a in an)/len(an) if an else 0
        cl="perf-excellent" if ab>=70 else "perf-good" if ab>=40 else "perf-warning" if ab>=20 else "perf-critical"
        st.markdown(f'<div class="perf-indicator {cl}">{"🔋" if ab>=40 else "🪫"} <strong>Battery:</strong> {ab:.1f}%</div>',unsafe_allow_html=True)
    with c3:
        ut=sum(1 for a in an if a["task_id"] is not None and not a["failed"])/len(an)*100 if an else 0
        cl="perf-excellent" if ut>=80 else "perf-good" if ut>=60 else "perf-warning" if ut>=30 else "perf-critical"
        st.markdown(f'<div class="perf-indicator {cl}">{"📈" if ut>=60 else "📉"} <strong>Utilization:</strong> {ut:.1f}%</div>',unsafe_allow_html=True)

with tab2:
    st.markdown("### 🤖 Fleet Status")
    an = st.session_state.agvs
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🟢 Idle",    sum(1 for a in an if not a["failed"] and a["task_id"] is None))
    c2.metric("🔵 Working", sum(1 for a in an if not a["failed"] and a["task_id"] is not None))
    c3.metric("🔴 Failed",  sum(1 for a in an if a["failed"]))
    c4.metric("🟡 Low Bat", sum(1 for a in an if a["battery"]<30 and not a["failed"]))

    for a in an:
        st_ = a.get("status", "idle")
        sm = {"idle":"Available","working":"Working","failed":"Failed","charging":"Charging","intercepting":"Intercepting"}
        sc = {"idle":"status-available","working":"status-working","failed":"status-failed",
              "charging":"status-charging","intercepting":"status-working"}
        sl=sm.get(st_,st_.capitalize()); ss=sc.get(st_,"status-available")
        bc="#ef4444" if a["battery"]<30 else "#10b981"
        with st.container():
            col1,col2,col3,col4 = st.columns([2,2,2,4])
            with col1:
                st.markdown(f"""<div class="fleet-card">
                  <h4 style="margin:0;color:#1e293b;">AGV-{a['id']:03d}</h4>
                  <p style="margin:5px 0;color:#64748b;">({a['x']:.1f},{a['y']:.1f})</p>
                  <span class="status-badge {ss}">{sl}</span></div>""",unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="fleet-card">
                  <div style="color:{bc};font-size:22px;font-weight:bold;">🔋{a['battery']:.1f}%</div>
                  <p style="margin:0;color:#64748b;font-size:12px;">Battery</p></div>""",unsafe_allow_html=True)
            with col3:
                tl=f"T-{a['task_id']}" if a["task_id"] is not None else "None"
                st.markdown(f"""<div class="fleet-card">
                  <div style="font-size:18px;font-weight:bold;color:#3b82f6;">📋{tl}</div>
                  <p style="margin:0;color:#64748b;font-size:12px;">Task</p></div>""",unsafe_allow_html=True)
            with col4:
                if a["failed"]:                 st.error(f"⚠️ {a.get('fault_type','Unknown')}")
                elif a.get("intercept"):        st.warning(f"⚡ {a['intercept']}")
                else:                           st.write(f"Tasks done: **{a.get('tasks_done',0)}**")

with tab3:
    st.markdown("### 🗺️ Live Digital Twin")
    # Serialize current Python state for the map
    agv_data = [{"id":a["id"],"x":a["x"],"y":a["y"],"battery":a["battery"],
                 "failed":a["failed"],"fault_type":a.get("fault_type"),
                 "intercept":a.get("intercept"),"task_id":a["task_id"],
                 "tasks_done":a.get("tasks_done",0),"status":a.get("status","idle")}
                for a in st.session_state.agvs]
    task_data = [{"id":t["id"],"x":t["x"],"y":t["y"],"priority":t["priority"],
                  "assigned_to":t["assigned_to"],"completed":t["completed"]}
                 for t in st.session_state.tasks]
    components.html(build_map_html(agv_data, task_data, GRID), height=720, scrolling=False)
    st.caption(f"🐍 Python simulation · Step {st.session_state.step_count} · "
               f"Completed {st.session_state.completed_count} tasks · Auto-reruns every cycle")

with tab4:
    st.markdown("### 📜 Event Log")
    ll = st.session_state.event_log
    c1,c2 = st.columns([3,1])
    with c1: flt=st.selectbox("Filter",["All","🚨 Faults","✅ Completions","⚡ Takeovers","🔄 Recoveries"])
    with c2: mx=st.number_input("Max",10,200,50)
    tm={"🚨 Faults":"fault","✅ Completions":"complete","⚡ Takeovers":"takeover","🔄 Recoveries":"recover"}
    fil=([l for l in ll if l.get("type")==tm[flt]] if flt in tm else ll)[:mx]
    cm={"fault":"#ef4444","takeover":"#f97316","complete":"#10b981","recover":"#9b59b6","assign":"#3b82f6"}
    st.markdown("<div class='log-container'>",unsafe_allow_html=True)
    for e in fil:
        ec=cm.get(e.get("type","assign"),"#64748b")
        st.markdown(
            f'<div style="margin:4px 0;padding:6px 10px;border-left:3px solid {ec};background:rgba(255,255,255,0.04);">'
            f'<span style="color:#94a3b8;">[{e.get("ts","")}]</span> '
            f'<span style="color:{ec};">●</span> {e.get("msg","")}</div>',
            unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🚨 Faults",     sum(1 for l in ll if l.get("type")=="fault"))
    c2.metric("⚡ Takeovers",   sum(1 for l in ll if l.get("type")=="takeover"))
    c3.metric("✅ Completions", sum(1 for l in ll if l.get("type")=="complete"))
    c4.metric("🔄 Recoveries",  sum(1 for l in ll if l.get("type")=="recover"))

with tab5:
    st.markdown("### 📈 Advanced Analytics")
    kh = st.session_state.kpi_history
    if len(kh) > 5:
        df = pd.DataFrame(kh)
        c1,c2 = st.columns(2)
        with c1:
            fs=px.scatter(df,x="availability",y="efficiency",size="avgbattery",color="utilization",
                title="🔍 Availability vs Efficiency",
                labels={"availability":"Fleet Avail (%)","efficiency":"Task Eff (%)"})
            fs.update_layout(height=380); st.plotly_chart(fs,use_container_width=True)
        with c2:
            r=df.tail(15); cols=["availability","efficiency","avgbattery","networkhealth"]
            fh=go.Figure(go.Heatmap(z=r[cols].values.T,x=r["step"].values,
                y=["Availability","Efficiency","Battery","Network"],
                colorscale="RdYlGn",texttemplate="%{z:.0f}",textfont={"size":9}))
            fh.update_layout(title="🌡️ Health Heatmap",height=380)
            st.plotly_chart(fh,use_container_width=True)
        st.markdown("#### 🔮 Predictive Insights")
        ins=[]
        if df.availability.tail(5).mean()<80: ins.append("⚠️ Fleet availability trending down — consider maintenance")
        if df.avgbattery.tail(5).mean()  <40: ins.append("🔋 Battery levels critically low")
        if df.efficiency.tail(5).mean()  <60: ins.append("📉 Task efficiency declining")
        if df.utilization.tail(5).mean() <50: ins.append("📊 Low utilization — too many idle AGVs")
        if not ins: ins.append("✅ System operating within normal parameters")
        for i in ins: st.info(i)
    else:
        st.info("📊 Simulation running... analytics appear after a few steps.")

# Footer
st.markdown("---")
c1,c2,c3,c4 = st.columns(4)
c1.markdown(f'<div style="text-align:center;padding:12px;"><h4 style="color:#64748b;margin:0;">🕒 Step</h4><div style="font-size:24px;font-weight:bold;color:#1e293b;">{st.session_state.step_count}</div></div>',unsafe_allow_html=True)
c2.markdown(f'<div style="text-align:center;padding:12px;"><h4 style="color:#64748b;margin:0;">✅ Done</h4><div style="font-size:24px;font-weight:bold;color:#10b981;">{st.session_state.completed_count}</div></div>',unsafe_allow_html=True)
an = st.session_state.agvs
c3.markdown(f'<div style="text-align:center;padding:12px;"><h4 style="color:#64748b;margin:0;">🤖 Active/Total</h4><div style="font-size:24px;font-weight:bold;color:#3b82f6;">{sum(1 for a in an if not a["failed"])}/{len(an)}</div></div>',unsafe_allow_html=True)
c4.markdown(f'<div style="text-align:center;padding:12px;"><h4 style="color:#64748b;margin:0;">⚡ Fault Rate</h4><div style="font-size:24px;font-weight:bold;color:#8b5cf6;">{FAULT_PROB*100:.0f}%</div></div>',unsafe_allow_html=True)

# ======================================
# 🔁 AUTO-RERUN (drives the simulation loop)
# ======================================
if st.session_state.sim_running:
    time.sleep(0.5)
    st.rerun()
