import streamlit as st
import streamlit.components.v1 as components
import requests as req
import random
import pandas as pd
import time
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="AGV Fleet Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================
# 🔐 FIREBASE AUTH
# ======================================
def firebase_login(email, password, action="login"):
    api_key = st.secrets["FIREBASE_KEY"]
    url = (f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
           if action == "signup"
           else f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}")
    return req.post(url, json={"email": email, "password": password, "returnSecureToken": True}).json()

def show_login():
    st.markdown("""
        <div style='text-align:center;margin-top:60px;margin-bottom:30px'>
            <h1>🤖➡️📦 AGV FLEET MANAGER</h1>
            <p style='color:#64748b;'>Sign in to access the dashboard</p>
        </div>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])
        with tab_login:
            email    = st.text_input("Email",    key="login_email",    placeholder="your@email.com")
            password = st.text_input("Password", key="login_password", placeholder="••••••••", type="password")
            if st.button("Login", key="login_btn", use_container_width=True):
                if email and password:
                    with st.spinner("Signing in..."):
                        result = firebase_login(email, password, "login")
                    if "idToken" in result:
                        st.session_state.update(user_email=result["email"],
                                                user_token=result["idToken"], logged_in=True)
                        st.rerun()
                    else:
                        msg = result.get("error", {}).get("message", "Login failed")
                        st.error("❌ Invalid email or password" if "EMAIL_NOT_FOUND" in msg or "INVALID_LOGIN_CREDENTIALS" in msg else f"❌ {msg}")
                else:
                    st.warning("⚠️ Please enter email and password")
        with tab_signup:
            ne  = st.text_input("Email",            key="signup_email",    placeholder="your@email.com")
            np_ = st.text_input("Password",         key="signup_password", placeholder="Min 6 chars", type="password")
            cp  = st.text_input("Confirm Password", key="confirm_password",                            type="password")
            if st.button("Create Account", key="signup_btn", use_container_width=True):
                if ne and np_ and cp:
                    if np_ != cp:        st.error("❌ Passwords do not match")
                    elif len(np_) < 6:   st.error("❌ Password must be ≥ 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            result = firebase_login(ne, np_, "signup")
                        if "idToken" in result:
                            st.session_state.update(user_email=result["email"],
                                                    user_token=result["idToken"], logged_in=True)
                            st.rerun()
                        else:
                            msg = result.get("error", {}).get("message", "Signup failed")
                            st.error("❌ Email already registered." if "EMAIL_EXISTS" in msg else f"❌ {msg}")
                else:
                    st.warning("⚠️ Please fill all fields")
    st.stop()

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
  box-shadow:0 4px 20px rgba(0,0,0,.08);border-left:4px solid;transition:all .3s ease;}
.critical-alert{background:linear-gradient(135deg,#fee2e2,#fef2f2);border-left-color:#dc2626;color:#991b1b;}
.warning-alert {background:linear-gradient(135deg,#fef3c7,#fffbeb);border-left-color:#d97706;color:#92400e;}
.success-alert {background:linear-gradient(135deg,#d1fae5,#f0fdf4);border-left-color:#059669;color:#065f46;}
.info-alert    {background:linear-gradient(135deg,#dbeafe,#eff6ff);border-left-color:#2563eb;color:#1d4ed8;}
.stButton>button{background:linear-gradient(135deg,#667eea,#764ba2)!important;color:white!important;
  border:none!important;border-radius:12px!important;padding:.5rem 1rem!important;font-weight:600!important;}
.stButton>button:hover{background:linear-gradient(135deg,#7c3aed,#8b5cf6)!important;}
.fleet-card{background:white;border-radius:16px;padding:16px;margin:8px 0;
  box-shadow:0 2px 10px rgba(0,0,0,.05);border:1px solid #e2e8f0;}
.status-badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;text-transform:uppercase;}
.status-available{background:#d1fae5;color:#065f46;} .status-working{background:#dbeafe;color:#1e40af;}
.status-failed   {background:#fee2e2;color:#991b1b;} .status-charging{background:#fef3c7;color:#92400e;}
.pulse-animation{animation:pulse 2s cubic-bezier(.4,0,.6,1) infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}
.control-section{background:white;border-radius:16px;padding:20px;margin:15px 0;
  box-shadow:0 4px 15px rgba(0,0,0,.05);border:1px solid #e2e8f0;}
div[data-testid="metric-container"]{background:linear-gradient(145deg,#fff,#f8fafc);
  border:1px solid #e2e8f0;padding:1rem;border-radius:16px;box-shadow:0 4px 15px rgba(0,0,0,.05);}
.log-container{background:#1e293b;color:#e2e8f0;padding:20px;border-radius:12px;
  font-family:'Monaco','Menlo',monospace;font-size:13px;line-height:1.5;max-height:400px;overflow-y:auto;}
.performance-indicator{display:flex;align-items:center;gap:8px;padding:8px 16px;border-radius:8px;font-weight:500;margin:4px 0;}
.perf-excellent{background:#d1fae5;color:#065f46;} .perf-good{background:#dbeafe;color:#1e40af;}
.perf-warning  {background:#fef3c7;color:#92400e;} .perf-critical{background:#fee2e2;color:#991b1b;}
.stTabs [data-baseweb="tab-list"]{gap:8px;background:transparent;}
.stTabs [data-baseweb="tab"]{height:50px;padding:0 24px;
  background:linear-gradient(135deg,#f8fafc,#fff);border-radius:12px;
  color:#64748b!important;font-weight:500;border:2px solid #e2e8f0;transition:all .3s ease;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#667eea,#764ba2)!important;
  color:white!important;border-color:transparent;box-shadow:0 6px 20px rgba(102,126,234,.4);}
.stSidebar>div{background:linear-gradient(180deg,#f8fafc,#fff);border-right:1px solid #e2e8f0;}
iframe{border:none!important;border-radius:16px;}
</style>
""", unsafe_allow_html=True)


# ======================================
# 🗃️ SESSION STATE INIT
# ======================================
GRIDSIZE  = 25
NUM_AGVS  = 10
NUM_TASKS = 18

def fresh_agvs():
    return [{"id":i,"x":round(random.uniform(0,GRIDSIZE),2),"y":round(random.uniform(0,GRIDSIZE),2),
             "battery":round(random.uniform(60,100),1),"failed":False,"faultType":None,
             "intercept":None,"taskId":None,"tasksDone":0,"status":"idle"} for i in range(NUM_AGVS)]

def fresh_tasks():
    return [{"id":i,"x":round(random.uniform(0,GRIDSIZE),2),"y":round(random.uniform(0,GRIDSIZE),2),
             "priority":random.choice([1,1,2,2,3]),"assignedTo":None,"completed":False} for i in range(NUM_TASKS)]

if "live_agvs" not in st.session_state:
    st.session_state.live_agvs       = fresh_agvs()
    st.session_state.live_tasks      = fresh_tasks()
    st.session_state.live_logs       = []
    st.session_state.completed_count = 0
    st.session_state.step_count      = 0
    st.session_state.kpi_history     = []


# ======================================
# 🔄 INGEST STATE PUSHED FROM MAP
# ======================================
def ingest_map_state(raw_json: str):
    try:
        data = json.loads(raw_json)
    except Exception:
        return
    if data.get("type") != "agv_state":
        return

    st.session_state.live_agvs       = data.get("agvs",  st.session_state.live_agvs)
    st.session_state.live_tasks      = data.get("tasks", st.session_state.live_tasks)
    st.session_state.completed_count = data.get("completedCount", st.session_state.completed_count)
    st.session_state.step_count      = data.get("stepCount",      st.session_state.step_count)

    new_logs = data.get("newLogs", [])
    if new_logs:
        st.session_state.live_logs = (new_logs + st.session_state.live_logs)[:300]

    # Compute KPI snapshot
    agvs  = st.session_state.live_agvs
    tasks = st.session_state.live_tasks
    n     = len(agvs) or 1
    ok    = sum(1 for a in agvs if not a["failed"])
    active= sum(1 for a in agvs if a.get("taskId") is not None and not a["failed"])
    done  = st.session_state.completed_count
    total_t = len(tasks) + done or 1

    st.session_state.kpi_history.append({
        "step":         st.session_state.step_count,
        "availability": round(ok / n * 100, 1),
        "avgbattery":   round(sum(a["battery"] for a in agvs) / n, 1),
        "utilization":  round(active / n * 100, 1),
        "efficiency":   round(done / total_t * 100, 1),
        "pendingtasks": sum(1 for t in tasks if not t.get("assignedTo") and not t.get("completed")),
        "networkhealth":round(ok / n * 100, 1),
    })
    if len(st.session_state.kpi_history) > 500:
        st.session_state.kpi_history = st.session_state.kpi_history[-500:]


# ======================================
# 🗺️  LIVE MAP HTML  (source of truth)
# ======================================
def build_live_map_html(agv_state, task_state, grid_size=25):
    agv_json  = json.dumps(agv_state)
    task_json = json.dumps(task_state)

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#020c18;--dim:#1a3a52;--accent:#00d4ff;--green:#00ff9d;
       --orange:#ff7b00;--red:#ff2d55;--yellow:#ffd700;--text:#7ec8e3}}
html,body{{width:100%;height:100%;overflow:hidden;background:var(--bg);
           color:var(--text);font-family:'Rajdhani',sans-serif}}
#wrap{{display:flex;flex-direction:column;height:100vh}}
header{{display:flex;align-items:center;justify-content:space-between;
        padding:8px 16px;border-bottom:1px solid var(--dim);
        background:rgba(0,15,30,.97);flex-shrink:0}}
.brand{{font-family:'Share Tech Mono',monospace;font-size:14px;color:var(--accent);letter-spacing:3px}}
.brand span{{color:var(--green)}}
.hstats{{display:flex;gap:16px}}
.stat{{text-align:center}}
.sv{{font-size:19px;font-weight:700;color:var(--accent);font-family:'Share Tech Mono',monospace;line-height:1}}
.sv.red{{color:var(--red)}} .sv.green{{color:var(--green)}} .sv.orange{{color:var(--orange)}}
.sl{{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#3a6a8a;margin-top:1px}}
.ctrls{{display:flex;gap:8px;align-items:center}}
button{{background:transparent;border:1px solid var(--accent);color:var(--accent);
        padding:5px 11px;font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;
        letter-spacing:1px;cursor:pointer;transition:all .2s;text-transform:uppercase;border-radius:3px}}
button:hover{{background:var(--accent);color:var(--bg)}}
button.active{{background:var(--accent);color:var(--bg)}}
button.danger{{border-color:var(--red);color:var(--red)}}
button.danger:hover{{background:var(--red);color:#fff}}
.spctl{{display:flex;align-items:center;gap:5px;font-size:11px}}
input[type=range]{{-webkit-appearance:none;height:3px;background:var(--dim);
                   border-radius:2px;outline:none;width:65px}}
input[type=range]::-webkit-slider-thumb{{-webkit-appearance:none;width:10px;height:10px;
  background:var(--accent);border-radius:50%;cursor:pointer}}
#sp-lbl{{font-family:'Share Tech Mono',monospace;color:var(--accent);font-size:11px;width:26px}}
.main{{display:flex;flex:1;overflow:hidden}}
#cvwrap{{flex:1;position:relative;overflow:hidden}}
canvas{{display:block;width:100%;height:100%}}
.sidebar{{width:220px;flex-shrink:0;background:rgba(0,10,22,.97);
          border-left:1px solid var(--dim);display:flex;flex-direction:column;overflow:hidden}}
.ssec{{padding:9px 11px;border-bottom:1px solid var(--dim)}}
.stitle{{font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#3a6a8a;margin-bottom:7px}}
.alist{{overflow-y:auto;padding:5px}}
.alist::-webkit-scrollbar{{width:3px}}
.alist::-webkit-scrollbar-thumb{{background:var(--dim);border-radius:2px}}
.acard{{background:rgba(0,20,40,.8);border:1px solid var(--dim);border-radius:3px;
        padding:7px;margin-bottom:5px;transition:border-color .3s}}
.acard.working{{border-color:rgba(0,212,255,.4)}}
.acard.failed{{border-color:rgba(255,45,85,.6);background:rgba(40,5,15,.8)}}
.acard.intercepting{{border-color:rgba(255,123,0,.6);background:rgba(30,15,0,.8)}}
.acard.charging{{border-color:rgba(255,215,0,.4)}}
.arow{{display:flex;justify-content:space-between;align-items:center;margin-bottom:3px}}
.aid{{font-family:'Share Tech Mono',monospace;font-size:11px;color:var(--accent)}}
.sdot{{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:3px}}
.bbar{{height:3px;background:var(--dim);border-radius:2px;overflow:hidden;margin-top:3px}}
.bfill{{height:100%;border-radius:2px;transition:width .5s}}
.ainfo{{font-size:10px;color:#3a6a8a;margin-top:2px}}
.ainfo.hl{{color:var(--orange);font-weight:600}}
.logp{{height:130px;overflow-y:auto;font-family:'Share Tech Mono',monospace;
       font-size:9px;padding:5px;background:rgba(0,5,12,.9);flex-shrink:0}}
.logp::-webkit-scrollbar{{width:2px}}
.logp::-webkit-scrollbar-thumb{{background:var(--dim)}}
.le{{padding:1px 0;border-bottom:1px solid rgba(26,58,82,.3);line-height:1.4}}
.le.fault{{color:var(--red)}} .le.takeover{{color:var(--orange)}}
.le.complete{{color:var(--green)}} .le.assign{{color:var(--accent)}} .le.recover{{color:#9b59b6}}
.legend{{display:flex;flex-wrap:wrap;gap:5px}}
.li{{display:flex;align-items:center;gap:3px;font-size:10px;color:#5a8aa5}}
.ld,.ls{{width:8px;height:8px}} .ld{{border-radius:50%}} .ls{{border-radius:2px}}
.tt{{position:absolute;background:rgba(0,10,22,.97);border:1px solid var(--accent);
     color:var(--text);padding:6px 9px;font-size:10px;pointer-events:none;
     border-radius:3px;display:none;white-space:nowrap;z-index:100;
     font-family:'Share Tech Mono',monospace}}
#sync-badge{{position:absolute;bottom:8px;right:8px;font-family:'Share Tech Mono',monospace;
             font-size:9px;color:var(--green);opacity:0;transition:opacity .4s;
             background:rgba(0,255,157,.1);border:1px solid var(--green);
             padding:3px 8px;border-radius:3px;pointer-events:none;letter-spacing:1px}}
#sync-badge.show{{opacity:1}}
</style></head>
<body>
<div id="wrap">
  <header>
    <div class="brand">AGV <span>LIVE</span> <span style="color:#3a6a8a;font-size:10px;margin-left:4px">▸ DRIVING DASHBOARD</span></div>
    <div class="hstats">
      <div class="stat"><div class="sv green"  id="s-active">0</div><div class="sl">Active</div></div>
      <div class="stat"><div class="sv red"    id="s-failed">0</div><div class="sl">Failed</div></div>
      <div class="stat"><div class="sv orange" id="s-intercept">0</div><div class="sl">Intercept</div></div>
      <div class="stat"><div class="sv"        id="s-tasks">0</div><div class="sl">Tasks</div></div>
      <div class="stat"><div class="sv green"  id="s-done">0</div><div class="sl">Done</div></div>
      <div class="stat"><div class="sv"        id="s-step">0</div><div class="sl">Step</div></div>
    </div>
    <div class="ctrls">
      <div class="spctl">
        <span style="font-size:9px;color:#3a6a8a;letter-spacing:1px">SPEED</span>
        <input type="range" id="spd" min="0.5" max="5" step="0.5" value="2">
        <span id="sp-lbl">2x</span>
      </div>
      <button id="btn-pause" class="active">⏸ PAUSE</button>
      <button id="btn-fault" class="danger">⚡ FAULT</button>
      <button id="btn-reset">↺ RESET</button>
    </div>
  </header>
  <div class="main">
    <div id="cvwrap">
      <canvas id="map"></canvas>
      <div class="tt" id="tt"></div>
      <div id="sync-badge">⬆ SYNCED TO DASHBOARD</div>
    </div>
    <div class="sidebar">
      <div class="ssec">
        <div class="stitle">Fleet Status</div>
        <div class="alist" id="alist" style="max-height:290px"></div>
      </div>
      <div class="ssec">
        <div class="stitle">Legend</div>
        <div class="legend">
          <div class="li"><div class="ld" style="background:#00ff9d"></div>Idle</div>
          <div class="li"><div class="ld" style="background:#00d4ff"></div>Working</div>
          <div class="li"><div class="ld" style="background:#ff7b00"></div>Intercept</div>
          <div class="li"><div class="ld" style="background:#ff2d55"></div>Failed</div>
          <div class="li"><div class="ld" style="background:#ffd700"></div>Low Batt</div>
          <div class="li"><div class="ls" style="background:#00ff9d"></div>P1</div>
          <div class="li"><div class="ls" style="background:#ffd700"></div>P2</div>
          <div class="li"><div class="ls" style="background:#ff2d55"></div>P3</div>
        </div>
      </div>
      <div class="ssec"><div class="stitle">Event Log</div></div>
      <div class="logp" id="logp"></div>
    </div>
  </div>
</div>

<script>
// ── Seed from Streamlit ───────────────────────────────────────────
const INIT_AGVS  = {agv_json};
const INIT_TASKS = {task_json};
const GRID       = {grid_size};
const NUM_AGVS   = INIT_AGVS.length  || 10;
const NUM_TASKS  = INIT_TASKS.length || 18;
const SYNC_MS    = 2000;   // push to Streamlit every 2s

const canvas = document.getElementById('map');
const ctx    = canvas.getContext('2d');
let running = true, speed = 2;
let completedCount = 0, stepCount = 0;
let stepAccum = 0, lastTime = 0, lastSyncTime = 0;
const STEP_MS = 500;
let taskIdCounter = 100000;
let logs = [], pendingLogs = [];

// ── Factories ─────────────────────────────────────────────────────
function makeAGV(s) {{
  return {{
    id: s.id,
    x:  typeof s.x       === 'number' ? s.x       : Math.random()*GRID,
    y:  typeof s.y       === 'number' ? s.y       : Math.random()*GRID,
    battery:  typeof s.battery  === 'number' ? s.battery  : (s.batterylevel ?? 80),
    failed:   !!s.failed,
    faultType: s.faultType || s.faulttype || null,
    intercept: s.intercept || null,
    task: null, lostTask: null,
    pathTrail: [], flashTimer: 0, recoveryTimer: 0,
    tasksDone: s.tasksDone || s.taskcompletioncount || 0,
  }};
}}
function newAGV(id) {{
  return makeAGV({{ id, x:Math.random()*GRID, y:Math.random()*GRID, battery:70+Math.random()*30 }});
}}
function makeTask(s) {{
  return {{
    id: s.id,
    x:  typeof s.x === 'number' ? s.x : Math.random()*GRID,
    y:  typeof s.y === 'number' ? s.y : Math.random()*GRID,
    priority:   s.priority || 1,
    assignedTo: null, completed: false, age: 0, sparkle: 0,
  }};
}}
function newTask(id) {{
  return makeTask({{ id, priority:[1,1,2,2,3][Math.floor(Math.random()*5)] }});
}}

let agvs  = INIT_AGVS.map(makeAGV);
let tasks = INIT_TASKS.map(makeTask);

function dist(a,b) {{ return Math.sqrt((a.x-b.x)**2+(a.y-b.y)**2); }}

// ── Logging ───────────────────────────────────────────────────────
function addLog(msg, type='assign') {{
  const ts = new Date().toLocaleTimeString('en',{{hour12:false}});
  const e  = {{msg,type,ts}};
  logs.unshift(e); pendingLogs.unshift(e);
  if (logs.length > 100) logs.pop();
  renderLog();
}}

// ── Simulation ────────────────────────────────────────────────────
function assignTasks() {{
  const free = tasks.filter(t=>!t.assignedTo&&!t.completed);
  const idle = agvs.filter(a=>!a.failed&&!a.task);
  free.sort((a,b)=>a.priority-b.priority);
  for (const t of free) {{
    if (!idle.length) break;
    const best = idle.reduce((b,a)=>dist(a,t)<dist(b,t)?a:b);
    t.assignedTo=best.id; best.task=t;
    idle.splice(idle.indexOf(best),1);
    addLog(`T-${{t.id}} → AGV-${{String(best.id).padStart(3,'0')}}`,'assign');
  }}
}}

function triggerTakeover(failedAGV) {{
  if (!failedAGV.lostTask) return;
  const cands = agvs.filter(a=>!a.failed&&!a.task&&a.id!==failedAGV.id);
  if (!cands.length) {{ addLog(`⚠️ No idle AGV for T-${{failedAGV.lostTask.id}}`,'fault'); return; }}
  const best = cands.reduce((b,a)=>dist(a,failedAGV.lostTask)<dist(b,failedAGV.lostTask)?a:b);
  const t = failedAGV.lostTask;
  t.assignedTo=best.id; best.task=t;
  best.intercept=`Takeover T-${{t.id}} ← AGV-${{failedAGV.id}}`;
  failedAGV.lostTask=null;
  addLog(`⚡ TAKEOVER: AGV-${{String(best.id).padStart(3,'0')}} → T-${{t.id}}`,'takeover');
}}

function triggerFault(agv) {{
  if (agv.failed) return;
  agv.failed=true;
  agv.faultType=['LiDAR Error','Motor Jam','Battery Crit','Comm Loss'][Math.floor(Math.random()*4)];
  agv.flashTimer=60;
  if (agv.task) {{
    agv.lostTask=agv.task; agv.task.assignedTo=null; agv.task=null;
    addLog(`🚨 AGV-${{String(agv.id).padStart(3,'0')}} FAULT: ${{agv.faultType}}`,'fault');
    triggerTakeover(agv);
  }} else addLog(`🚨 AGV-${{String(agv.id).padStart(3,'0')}} FAULT: ${{agv.faultType}}`,'fault');
  agv.recoveryTimer=180+Math.random()*120;
}}

function stepSim() {{
  stepCount++;
  for (const a of agvs) if (!a.failed && Math.random()<0.015) triggerFault(a);

  for (const a of agvs) {{
    if (!a.failed) continue;
    a.recoveryTimer--;
    if (a.recoveryTimer<=0) {{
      a.failed=false; a.faultType=null; a.intercept=null;
      addLog(`✅ AGV-${{String(a.id).padStart(3,'0')}} recovered`,'recover');
    }}
  }}

  for (const a of agvs) {{
    if (a.failed||!a.task) continue;
    const t=a.task, dx=t.x-a.x, dy=t.y-a.y, d=Math.sqrt(dx*dx+dy*dy), step=0.35*speed;
    if (d<step) {{
      a.x=t.x; a.y=t.y; t.completed=true; completedCount++;
      a.task=null; a.intercept=null; a.tasksDone++;
      t.sparkle=30;
      addLog(`✅ T-${{t.id}} done by AGV-${{String(a.id).padStart(3,'0')}}`,'complete');
    }} else {{ a.x+=dx/d*step; a.y+=dy/d*step; }}
    a.battery=Math.max(0,a.battery-0.03*speed);
    a.pathTrail.push({{x:a.x,y:a.y}});
    if (a.pathTrail.length>40) a.pathTrail.shift();
  }}

  for (const a of agvs)
    if (!a.task&&!a.failed&&a.battery<100) a.battery=Math.min(100,a.battery+0.2*speed);

  assignTasks();
  tasks=tasks.filter(t=>!t.completed);
  while (tasks.length<NUM_TASKS) {{
    const nt=newTask(taskIdCounter++);
    tasks.push(nt); nt.sparkle=20;
    addLog(`🆕 T-${{nt.id}} spawned`,'assign');
  }}
}}

// ── Push state to Streamlit via postMessage ───────────────────────
function syncToStreamlit() {{
  const now = Date.now();
  if (now-lastSyncTime < SYNC_MS) return;
  lastSyncTime = now;

  const payload = {{
    type: 'agv_state',
    agvs: agvs.map(a => ({{
      id:        a.id,
      x:         parseFloat(a.x.toFixed(2)),
      y:         parseFloat(a.y.toFixed(2)),
      battery:   parseFloat(a.battery.toFixed(1)),
      failed:    a.failed,
      faultType: a.faultType,
      intercept: a.intercept,
      taskId:    a.task ? a.task.id : null,
      tasksDone: a.tasksDone,
      status:    a.failed?'failed':a.intercept?'intercepting':a.task?'working':a.battery<30?'charging':'idle',
    }})),
    tasks: tasks.map(t => ({{
      id:t.id, x:parseFloat(t.x.toFixed(2)), y:parseFloat(t.y.toFixed(2)),
      priority:t.priority, assignedTo:t.assignedTo, completed:t.completed,
    }})),
    completedCount, stepCount,
    newLogs: pendingLogs.splice(0, 40),
  }};

  // Post to parent Streamlit window
  window.parent.postMessage(payload, '*');

  const badge = document.getElementById('sync-badge');
  badge.classList.add('show');
  setTimeout(()=>badge.classList.remove('show'), 700);
}}

// ── Canvas rendering ──────────────────────────────────────────────
let cw,ch,cellW,cellH,padX,padY;
function resize() {{
  const w=document.getElementById('cvwrap');
  cw=canvas.width=w.clientWidth; ch=canvas.height=w.clientHeight;
  const sz=Math.min(cw,ch)*.92;
  cellW=sz/GRID; cellH=sz/GRID;
  padX=(cw-sz)/2; padY=(ch-sz)/2;
}}
const tx=v=>padX+v*cellW, ty=v=>padY+v*cellH;

function drawGrid() {{
  ctx.strokeStyle='rgba(10,31,53,0.8)'; ctx.lineWidth=0.5;
  for(let i=0;i<=GRID;i++) {{
    ctx.beginPath();ctx.moveTo(tx(i),ty(0));ctx.lineTo(tx(i),ty(GRID));ctx.stroke();
    ctx.beginPath();ctx.moveTo(tx(0),ty(i));ctx.lineTo(tx(GRID),ty(i));ctx.stroke();
  }}
  ctx.strokeStyle='rgba(0,212,255,0.04)'; ctx.lineWidth=0.4;
  for(let i=5;i<GRID;i+=5) {{
    ctx.beginPath();ctx.moveTo(tx(i),ty(0));ctx.lineTo(tx(i),ty(GRID));ctx.stroke();
    ctx.beginPath();ctx.moveTo(tx(0),ty(i));ctx.lineTo(tx(GRID),ty(i));ctx.stroke();
  }}
}}

function drawTasks() {{
  for(const t of tasks) {{
    const px=tx(t.x),py=ty(t.y),col={{1:'#00ff9d',2:'#ffd700',3:'#ff2d55'}}[t.priority];
    t.age++;
    if(t.sparkle>0){{
      t.sparkle--;
      ctx.strokeStyle=col;ctx.globalAlpha=t.sparkle/20;ctx.lineWidth=2;
      ctx.beginPath();ctx.arc(px,py,(20-t.sparkle/20*20)+5,0,Math.PI*2);ctx.stroke();
      ctx.globalAlpha=1;
    }}
    const pulse=0.5+0.5*Math.sin(Date.now()*.003+t.id);
    ctx.shadowBlur=8+pulse*6;ctx.shadowColor=col;
    const s=cellW*.55;
    ctx.fillStyle=col;ctx.globalAlpha=.15+pulse*.05;
    ctx.fillRect(px-s/2,py-s/2,s,s);ctx.globalAlpha=1;ctx.shadowBlur=0;
    ctx.strokeStyle=col;ctx.lineWidth=1.5;ctx.globalAlpha=.8;
    ctx.strokeRect(px-s/2,py-s/2,s,s);ctx.globalAlpha=1;
    ctx.fillStyle=col;ctx.font=`bold ${{cellW*.35}}px Rajdhani`;
    ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(`P${{t.priority}}`,px,py);
    ctx.fillStyle='rgba(255,255,255,0.3)';ctx.font=`${{cellW*.2}}px Share Tech Mono`;
    ctx.fillText(`T${{t.id}}`,px,py+s/2+8);
  }}
}}

function drawTrails() {{
  for(const a of agvs) {{
    if(a.failed||a.pathTrail.length<2) continue;
    const col=a.intercept?'#ff7b00':'#00d4ff';
    for(let i=1;i<a.pathTrail.length;i++) {{
      ctx.strokeStyle=col;ctx.globalAlpha=(i/a.pathTrail.length)*.4;ctx.lineWidth=1.5;
      ctx.beginPath();
      ctx.moveTo(tx(a.pathTrail[i-1].x),ty(a.pathTrail[i-1].y));
      ctx.lineTo(tx(a.pathTrail[i].x),ty(a.pathTrail[i].y));ctx.stroke();
    }}
    ctx.globalAlpha=1;
  }}
}}

function drawLines() {{
  for(const a of agvs) {{
    if(!a.task||a.failed) continue;
    const ax=tx(a.x),ay=ty(a.y),bx=tx(a.task.x),by=ty(a.task.y);
    const col=a.intercept?'#ff7b00':'rgba(0,212,255,0.25)';
    ctx.strokeStyle=col;ctx.setLineDash([4,6]);
    ctx.lineWidth=a.intercept?1.5:1;ctx.globalAlpha=a.intercept?.8:.5;
    ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(bx,by);ctx.stroke();
    ctx.setLineDash([]);ctx.globalAlpha=1;
    const angle=Math.atan2(by-ay,bx-ax),mid={{x:(ax+bx)/2,y:(ay+by)/2}};
    ctx.fillStyle=col;ctx.globalAlpha=.7;
    ctx.save();ctx.translate(mid.x,mid.y);ctx.rotate(angle);
    ctx.beginPath();ctx.moveTo(5,0);ctx.lineTo(-4,4);ctx.lineTo(-4,-4);
    ctx.closePath();ctx.fill();ctx.restore();ctx.globalAlpha=1;
  }}
}}

function drawAGVs() {{
  const R=cellW*.55;
  for(const a of agvs) {{
    const px=tx(a.x),py=ty(a.y);
    if(a.flashTimer>0) a.flashTimer--;
    let col,ring;
    if     (a.failed)       {{col='#ff2d55';ring='rgba(255,45,85,0.3)';}}
    else if(a.intercept)    {{col='#ff7b00';ring='rgba(255,123,0,0.3)';}}
    else if(a.task)         {{col='#00d4ff';ring='rgba(0,212,255,0.2)';}}
    else if(a.battery<30)   {{col='#ffd700';ring='rgba(255,215,0,0.2)';}}
    else                    {{col='#00ff9d';ring='rgba(0,255,157,0.15)';}}
    const pulse=0.5+0.5*Math.sin(Date.now()*.004+a.id*.7);
    ctx.beginPath();ctx.arc(px,py,R*(1.4+pulse*.3),0,Math.PI*2);
    ctx.fillStyle=ring;ctx.fill();
    ctx.shadowBlur=a.failed?20:(a.intercept?18:12);ctx.shadowColor=col;
    ctx.beginPath();ctx.arc(px,py,R,0,Math.PI*2);
    ctx.fillStyle=col+'22';ctx.fill();
    ctx.strokeStyle=col;ctx.lineWidth=2;ctx.stroke();ctx.shadowBlur=0;
    ctx.beginPath();ctx.arc(px,py,R*.35,0,Math.PI*2);ctx.fillStyle=col;ctx.fill();
    ctx.fillStyle=a.failed?'#ff2d55':'#ffffff';
    ctx.font=`bold ${{R*.65}}px Rajdhani`;ctx.textAlign='center';ctx.textBaseline='middle';
    ctx.fillText(a.id,px,py);
    const bw=R*1.8;
    ctx.fillStyle='#0a1f35';ctx.fillRect(px-bw/2,py+R+3,bw,3);
    const bc=a.battery>50?'#00ff9d':a.battery>20?'#ffd700':'#ff2d55';
    ctx.fillStyle=bc;ctx.fillRect(px-bw/2,py+R+3,bw*(a.battery/100),3);
    if(a.failed){{
      ctx.strokeStyle='#ff2d55';ctx.lineWidth=2;const x=R*.5;
      ctx.beginPath();ctx.moveTo(px-x,py-x);ctx.lineTo(px+x,py+x);ctx.stroke();
      ctx.beginPath();ctx.moveTo(px+x,py-x);ctx.lineTo(px-x,py+x);ctx.stroke();
    }}
    if(a.intercept&&!a.failed){{
      ctx.fillStyle='#ff7b00';ctx.font=`${{R*.7}}px Rajdhani`;
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText('⚡',px+R+4,py-R);
    }}
  }}
}}

function frame(ts) {{
  if(!running){{lastTime=ts;requestAnimationFrame(frame);return;}}
  const dt=ts-lastTime;lastTime=ts;
  stepAccum+=dt;
  if(stepAccum>=STEP_MS/speed){{
    stepAccum=0;
    stepSim();
    updateSidebar();
    syncToStreamlit();
  }}
  ctx.clearRect(0,0,cw,ch);
  const g=ctx.createRadialGradient(cw/2,ch/2,0,cw/2,ch/2,Math.max(cw,ch)/2);
  g.addColorStop(0,'#020c18');g.addColorStop(1,'#010810');
  ctx.fillStyle=g;ctx.fillRect(0,0,cw,ch);
  drawGrid();drawTrails();drawLines();drawTasks();drawAGVs();
  requestAnimationFrame(frame);
}}

// ── Sidebar ───────────────────────────────────────────────────────
function updateSidebar() {{
  document.getElementById('s-active').textContent    = agvs.filter(a=>!a.failed&&a.task).length;
  document.getElementById('s-failed').textContent    = agvs.filter(a=>a.failed).length;
  document.getElementById('s-intercept').textContent = agvs.filter(a=>a.intercept&&!a.failed).length;
  document.getElementById('s-tasks').textContent     = tasks.length;
  document.getElementById('s-done').textContent      = completedCount;
  document.getElementById('s-step').textContent      = stepCount;
  document.getElementById('alist').innerHTML = agvs.map(a=>{{
    let cls='acard',dot='#00ff9d',lbl='IDLE';
    if(a.failed){{cls+=' failed';dot='#ff2d55';lbl='FAILED';}}
    else if(a.intercept){{cls+=' intercepting';dot='#ff7b00';lbl='INTERCEPT';}}
    else if(a.task){{cls+=' working';dot='#00d4ff';lbl='WORKING';}}
    else if(a.battery<30){{cls+=' charging';dot='#ffd700';lbl='CHARGING';}}
    const bc=a.battery>50?'#00ff9d':a.battery>20?'#ffd700':'#ff2d55';
    const info=a.failed
      ?`<div class="ainfo" style="color:#ff2d55">⚠️ ${{a.faultType}}</div>`
      :a.intercept?`<div class="ainfo hl">⚡ ${{a.intercept}}</div>`
      :a.task?`<div class="ainfo">→ T-${{a.task.id}} (${{a.x.toFixed(1)}},${{a.y.toFixed(1)}})</div>`
      :`<div class="ainfo">Done: ${{a.tasksDone}}</div>`;
    return `<div class="${{cls}}">
      <div class="arow">
        <span class="aid"><span class="sdot" style="background:${{dot}}"></span>AGV-${{String(a.id).padStart(3,'0')}}</span>
        <span style="font-size:9px;letter-spacing:1px;color:${{dot}}">${{lbl}}</span>
      </div>
      <div class="bbar"><div class="bfill" style="width:${{a.battery}}%;background:${{bc}}"></div></div>
      <div class="arow" style="margin-top:2px">
        <span style="font-size:9px;color:#3a6a8a">🔋${{a.battery.toFixed(0)}}%</span>
        <span style="font-size:9px;color:#3a6a8a">(${{a.x.toFixed(0)}},${{a.y.toFixed(0)}})</span>
      </div>${{info}}</div>`;
  }}).join('');
}}

function renderLog() {{
  document.getElementById('logp').innerHTML=logs.slice(0,60).map(l=>
    `<div class="le ${{l.type}}"><span style="color:#1a4a6a">[${{l.ts}}]</span> ${{l.msg}}</div>`
  ).join('');
}}

// ── Controls ──────────────────────────────────────────────────────
document.getElementById('btn-pause').addEventListener('click',function(){{
  running=!running;this.textContent=running?'⏸ PAUSE':'▶ PLAY';
  this.classList.toggle('active',running);
}});
document.getElementById('btn-fault').addEventListener('click',()=>{{
  const a=agvs.filter(x=>!x.failed);
  if(a.length) triggerFault(a[Math.floor(Math.random()*a.length)]);
}});
document.getElementById('btn-reset').addEventListener('click',()=>{{
  completedCount=0;stepCount=0;pendingLogs=[];logs=[];
  agvs=INIT_AGVS.map(makeAGV);tasks=INIT_TASKS.map(makeTask);
  addLog('🔄 System reset','assign');assignTasks();updateSidebar();
}});
document.getElementById('spd').addEventListener('input',function(){{
  speed=parseFloat(this.value);
  document.getElementById('sp-lbl').textContent=speed+'x';
}});

// ── Tooltip ───────────────────────────────────────────────────────
canvas.addEventListener('mousemove',e=>{{
  const r=canvas.getBoundingClientRect();
  const wx=((e.clientX-r.left)*(cw/r.width)-padX)/cellW;
  const wy=((e.clientY-r.top)*(ch/r.height)-padY)/cellH;
  const tt=document.getElementById('tt');
  let f=null;
  for(const a of agvs) if(dist({{x:wx,y:wy}},a)<1.2){{f={{t:'agv',d:a}};break;}}
  if(!f) for(const t of tasks) if(dist({{x:wx,y:wy}},t)<0.8){{f={{t:'task',d:t}};break;}}
  if(f){{
    const d=f.d;
    tt.innerHTML=f.t==='agv'
      ?`AGV-${{String(d.id).padStart(3,'0')}}<br>🔋${{d.battery.toFixed(1)}}%<br>${{d.failed?d.faultType:d.intercept?'INTERCEPT':d.task?'WORKING':'IDLE'}}<br>Done:${{d.tasksDone}}`
      :`T-${{d.id}} P${{d.priority}}<br>Assigned:${{d.assignedTo!=null?'AGV-'+String(d.assignedTo).padStart(3,'0'):'None'}}`;
    tt.style.cssText=`display:block;left:${{e.clientX+14}}px;top:${{e.clientY-8}}px`;
  }} else tt.style.display='none';
}});
canvas.addEventListener('mouseleave',()=>document.getElementById('tt').style.display='none');

// ── Init ──────────────────────────────────────────────────────────
window.addEventListener('resize',resize);
resize();assignTasks();updateSidebar();
addLog('🚀 Live map started — driving Streamlit','assign');
requestAnimationFrame(frame);
</script>
</body></html>"""


# ======================================
# 🔌 postMessage bridge snippet
# This is injected as a SEPARATE components.html call (height=0).
# It lives in the Streamlit page (not inside the iframe) so it can
# receive the iframe's postMessage and write to the hidden input.
# ======================================
BRIDGE_SNIPPET = """
<script>
(function() {
  function findBridgeInput() {
    // Find the hidden text input we tagged with data-bridge
    return document.querySelector('input[data-bridge="agv_state"]');
  }

  window.addEventListener('message', function(e) {
    if (!e.data || e.data.type !== 'agv_state') return;
    var inp = findBridgeInput();
    if (!inp) return;
    var json = JSON.stringify(e.data);
    // Use React's native setter so Streamlit detects the change
    var nativeSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype, 'value').set;
    nativeSetter.call(inp, json);
    inp.dispatchEvent(new Event('input', { bubbles: true }));
  }, false);

  // Tag our bridge input after a short delay (DOM must exist)
  setTimeout(function() {
    var all = document.querySelectorAll('input[type="text"]');
    // The bridge input is rendered with a specific aria-label we set
    for (var i = 0; i < all.length; i++) {
      if (all[i].getAttribute('aria-label') === '__agv_bridge__') {
        all[i].setAttribute('data-bridge', 'agv_state');
        break;
      }
    }
  }, 800);
})();
</script>
"""


# ======================================
# 🖥️ HEADER
# ======================================
st.markdown("""
<div class="main-header">
  <h1 style="margin:0;font-size:2.5rem;font-weight:700;">🤖 AGV Fleet Management System</h1>
  <p style="margin:10px 0 0 0;font-size:1.1rem;opacity:.9;">
    Live Map Simulation → Streamlit Dashboard &nbsp;·&nbsp; Real-time Fleet Operations
  </p>
</div>
""", unsafe_allow_html=True)

# ======================================
# 🔗 Hidden bridge input + listener
# ======================================
# Rendered before everything else so the DOM element exists early.
bridge_raw = st.text_input("__agv_bridge__", key="map_state_bridge", label_visibility="collapsed")
components.html(BRIDGE_SNIPPET, height=0)

# Ingest immediately if we have new data
if bridge_raw:
    ingest_map_state(bridge_raw)
    # Clear so the same value doesn't re-trigger on next static rerun
    # (Streamlit will rerun when the input changes, which is what we want)

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
    st.markdown("### 📊 Live Fleet Status")
    agvs_now = st.session_state.live_agvs
    c1, c2 = st.columns(2)
    c1.metric("🟢 Active",   sum(1 for a in agvs_now if not a["failed"] and a.get("taskId") is not None))
    c2.metric("🔴 Failed",   sum(1 for a in agvs_now if a["failed"]))
    c1.metric("⚡ Intercept",sum(1 for a in agvs_now if a.get("intercept") and not a["failed"]))
    c2.metric("✅ Done",     st.session_state.completed_count)

    if st.session_state.kpi_history:
        lk = st.session_state.kpi_history[-1]
        av = lk["availability"]
        color = "#10b981" if av >= 90 else "#f59e0b" if av >= 70 else "#ef4444"
        label = "Excellent"  if av >= 90 else "Good" if av >= 70 else "Critical"
        st.markdown(f"""
        <div style="text-align:center;padding:14px;background:white;border-radius:12px;margin-top:10px;">
          <div style="font-size:24px;font-weight:bold;color:{color};">{av:.1f}%</div>
          <div style="color:#64748b;">Fleet Availability</div>
          <div style="margin-top:6px;padding:3px 10px;background:{color}20;
               color:{color};border-radius:20px;font-weight:600;font-size:12px;">{label.upper()}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='control-section'>", unsafe_allow_html=True)
    st.markdown("### ℹ️ Architecture")
    st.markdown("""
**Live Map** is the simulation engine.

Every **2 s** it pushes state to Streamlit via `postMessage`:
- AGV positions & battery
- Fault & takeover events
- Task completions & spawns

Dashboard, Fleet Status, Analytics and Event Log all update from this live data. No separate Python simulation loop.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# KPI banner
if st.session_state.kpi_history:
    lk = st.session_state.kpi_history[-1]
    av = lk["availability"]
    if av >= 90:
        st.markdown(f'<div class="status-card success-alert"><strong>🟢 System Excellent</strong> · Availability {av:.1f}% · Step {lk["step"]}</div>', unsafe_allow_html=True)
    elif av >= 70:
        st.markdown(f'<div class="status-card warning-alert"><strong>🟡 System Good</strong> · Availability {av:.1f}% · Step {lk["step"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-card critical-alert pulse-animation"><strong>🔴 System Critical</strong> · Availability {av:.1f}% · Step {lk["step"]}</div>', unsafe_allow_html=True)

# ======================================
# 📑 TABS
# ======================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Dashboard", "🤖 Fleet Status", "🗺️ Live Map", "📜 Event Log", "📈 Analytics"])

# ── TAB 1 ────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 📊 Real-time Performance Dashboard")
    kh = st.session_state.kpi_history
    if kh:
        lk = kh[-1]; pk = kh[-2] if len(kh) > 1 else lk
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("🎯 Fleet Availability", f"{lk['availability']:.1f}%",  f"{lk['availability']-pk['availability']:.1f}%")
        c2.metric("🔋 Avg Battery",        f"{lk['avgbattery']:.1f}%",   f"{lk['avgbattery']-pk['avgbattery']:.1f}%")
        c3.metric("🌐 Network Health",      f"{lk['networkhealth']:.0f}%",f"{lk['networkhealth']-pk['networkhealth']:.1f}%")
        c4.metric("📋 Pending Tasks",       lk['pendingtasks'],            int(lk['pendingtasks']-pk['pendingtasks']), delta_color="inverse")
        c5.metric("⚡ Utilization",         f"{lk['utilization']:.1f}%",  f"{lk['utilization']-pk['utilization']:.1f}%")

    if len(kh) > 2:
        st.markdown("### 📈 Performance Trends")
        df = pd.DataFrame(kh)
        fig = make_subplots(rows=2, cols=3,
            subplot_titles=("🎯 Fleet Availability","⚡ Utilization","✅ Task Efficiency",
                            "🌐 Network Health","🔋 Avg Battery","📋 Pending Tasks"),
            vertical_spacing=0.12, horizontal_spacing=0.08)
        kw = dict(mode="lines+markers", marker=dict(size=5))
        fig.add_trace(go.Scatter(x=df.step, y=df.availability,  line=dict(color='#10b981',width=2), **kw), row=1,col=1)
        fig.add_trace(go.Scatter(x=df.step, y=df.utilization,   line=dict(color='#f59e0b',width=2), **kw), row=1,col=2)
        fig.add_trace(go.Scatter(x=df.step, y=df.efficiency,    line=dict(color='#3b82f6',width=2), **kw), row=2,col=1)
        fig.add_trace(go.Scatter(x=df.step, y=df.networkhealth, line=dict(color='#8b5cf6',width=2), **kw), row=2,col=2)
        fig.add_trace(go.Scatter(x=df.step, y=df.avgbattery,    line=dict(color='#06b6d4',width=2), **kw), row=2,col=3)
        fig.add_trace(go.Bar(x=df.step, y=df.pendingtasks, marker=dict(color='#ef4444',opacity=0.7)), row=1,col=3)
        fig.update_layout(height=560, showlegend=False, plot_bgcolor='white', paper_bgcolor='white')
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e2e8f0')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏥 System Health")
    c1,c2,c3 = st.columns(3)
    agvs_now = st.session_state.live_agvs
    with c1:
        ok = sum(1 for a in agvs_now if not a["failed"]); hs = ok/len(agvs_now)*100 if agvs_now else 0
        cl = "perf-excellent" if hs>=90 else "perf-good" if hs>=70 else "perf-warning" if hs>=50 else "perf-critical"
        ic = "🟢" if hs>=90 else "🟡" if hs>=70 else "🟠" if hs>=50 else "🔴"
        st.markdown(f'<div class="performance-indicator {cl}">{ic} <strong>Overall Health:</strong> {hs:.1f}%</div>', unsafe_allow_html=True)
    with c2:
        ab = sum(a["battery"] for a in agvs_now)/len(agvs_now) if agvs_now else 0
        cl = "perf-excellent" if ab>=70 else "perf-good" if ab>=40 else "perf-warning" if ab>=20 else "perf-critical"
        st.markdown(f'<div class="performance-indicator {cl}">{"🔋" if ab>=40 else "🪫"} <strong>Battery Status:</strong> {ab:.1f}%</div>', unsafe_allow_html=True)
    with c3:
        ut = sum(1 for a in agvs_now if a.get("taskId") is not None and not a["failed"])/len(agvs_now)*100 if agvs_now else 0
        cl = "perf-excellent" if ut>=80 else "perf-good" if ut>=60 else "perf-warning" if ut>=30 else "perf-critical"
        st.markdown(f'<div class="performance-indicator {cl}">{"📈" if ut>=60 else "📉"} <strong>Utilization:</strong> {ut:.1f}%</div>', unsafe_allow_html=True)

# ── TAB 2 ────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🤖 Fleet Status — Driven by Live Map")
    agvs_now = st.session_state.live_agvs
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🟢 Idle",     sum(1 for a in agvs_now if not a["failed"] and a.get("taskId") is None))
    c2.metric("🔵 Working",  sum(1 for a in agvs_now if not a["failed"] and a.get("taskId") is not None))
    c3.metric("🔴 Failed",   sum(1 for a in agvs_now if a["failed"]))
    c4.metric("🟡 Low Batt", sum(1 for a in agvs_now if a["battery"] < 30 and not a["failed"]))

    for a in agvs_now:
        st_ = a.get("status","idle")
        s_map  = {"idle":"Available","working":"Working","failed":"Failed",
                  "charging":"Charging","intercepting":"Intercepting"}
        s_cls  = {"idle":"status-available","working":"status-working","failed":"status-failed",
                  "charging":"status-charging","intercepting":"status-working"}
        sl = s_map.get(st_, st_.capitalize())
        sc = s_cls.get(st_, "status-available")
        bc = "#ef4444" if a["battery"] < 30 else "#10b981"
        with st.container():
            col1,col2,col3,col4 = st.columns([2,2,2,4])
            with col1:
                st.markdown(f"""<div class="fleet-card">
                  <h4 style="margin:0;color:#1e293b;">AGV-{a['id']:03d}</h4>
                  <p style="margin:5px 0;color:#64748b;">({a['x']:.1f}, {a['y']:.1f})</p>
                  <span class="status-badge {sc}">{sl}</span></div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="fleet-card">
                  <div style="color:{bc};font-size:22px;font-weight:bold;">🔋 {a['battery']:.1f}%</div>
                  <p style="margin:0;color:#64748b;font-size:12px;">Battery</p></div>""", unsafe_allow_html=True)
            with col3:
                tl = f"T-{a['taskId']}" if a.get("taskId") is not None else "None"
                st.markdown(f"""<div class="fleet-card">
                  <div style="font-size:18px;font-weight:bold;color:#3b82f6;">📋 {tl}</div>
                  <p style="margin:0;color:#64748b;font-size:12px;">Current Task</p></div>""", unsafe_allow_html=True)
            with col4:
                if a["failed"]:           st.error(f"⚠️ {a.get('faultType','Unknown fault')}")
                elif a.get("intercept"):  st.warning(f"⚡ {a['intercept']}")
                else:                     st.write(f"Tasks completed: **{a.get('tasksDone',0)}**")

# ── TAB 3 ────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 🗺️ Live Digital Twin — Source of Truth")
    live_html = build_live_map_html(
        st.session_state.live_agvs,
        st.session_state.live_tasks,
        GRIDSIZE
    )
    components.html(live_html, height=730, scrolling=False)
    st.caption("⬆ Map pushes state to Streamlit every 2 s via postMessage → all other tabs update automatically.")

# ── TAB 4 ────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 📜 Live Event Log — from Map Simulation")
    ll = st.session_state.live_logs
    c1,c2 = st.columns([3,1])
    with c1: filt = st.selectbox("Filter",["All","🚨 Faults","✅ Completions","⚡ Takeovers","🔄 Recoveries"])
    with c2: max_e = st.number_input("Max", 10, 200, 50)

    type_map = {"🚨 Faults":"fault","✅ Completions":"complete",
                "⚡ Takeovers":"takeover","🔄 Recoveries":"recover"}
    filtered = ([l for l in ll if l.get("type")==type_map[filt]] if filt in type_map else ll)[:max_e]

    st.markdown("<div class='log-container'>", unsafe_allow_html=True)
    color_map = {"fault":"#ef4444","takeover":"#f97316","complete":"#10b981","recover":"#9b59b6","assign":"#3b82f6"}
    for entry in filtered:
        ec = color_map.get(entry.get("type","assign"),"#64748b")
        st.markdown(
            f'<div style="margin:4px 0;padding:6px 10px;border-left:3px solid {ec};background:rgba(255,255,255,0.04);">'
            f'<span style="color:#94a3b8;">[{entry.get("ts","")}]</span> '
            f'<span style="color:{ec};">●</span> {entry.get("msg","")}</div>',
            unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🚨 Faults",     sum(1 for l in ll if l.get("type")=="fault"))
    c2.metric("⚡ Takeovers",   sum(1 for l in ll if l.get("type")=="takeover"))
    c3.metric("✅ Completions", sum(1 for l in ll if l.get("type")=="complete"))
    c4.metric("🔄 Recoveries",  sum(1 for l in ll if l.get("type")=="recover"))

# ── TAB 5 ────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📈 Advanced Analytics")
    kh = st.session_state.kpi_history
    if len(kh) > 5:
        df = pd.DataFrame(kh)
        c1,c2 = st.columns(2)
        with c1:
            fig_s = px.scatter(df, x="availability", y="efficiency", size="avgbattery",
                color="utilization", title="🔍 Availability vs Efficiency",
                labels={"availability":"Fleet Avail (%)","efficiency":"Task Eff (%)"})
            fig_s.update_layout(height=380)
            st.plotly_chart(fig_s, use_container_width=True)
        with c2:
            recent = df.tail(15)
            cols = ["availability","efficiency","avgbattery","networkhealth"]
            fig_h = go.Figure(go.Heatmap(
                z=recent[cols].values.T, x=recent["step"].values,
                y=["Availability","Efficiency","Avg Battery","Network Health"],
                colorscale="RdYlGn", texttemplate="%{z:.0f}", textfont={"size":9}))
            fig_h.update_layout(title="🌡️ System Health Heatmap", height=380)
            st.plotly_chart(fig_h, use_container_width=True)

        st.markdown("#### 🔮 Predictive Insights")
        insights = []
        if df.availability.tail(5).mean() < 80:  insights.append("⚠️ Fleet availability trending down — consider maintenance scheduling")
        if df.avgbattery.tail(5).mean()   < 40:  insights.append("🔋 Battery levels critically low — implement charging strategy")
        if df.efficiency.tail(5).mean()   < 60:  insights.append("📉 Task efficiency declining — review assignment algorithm")
        if df.utilization.tail(5).mean()  < 50:  insights.append("📊 Low utilization — too many idle AGVs")
        if not insights:                          insights.append("✅ System operating within normal parameters")
        for i in insights: st.info(i)
    else:
        st.info("📊 Let the map run for ~10 seconds to accumulate enough data for analytics.")

# ======================================
# 🦶 FOOTER
# ======================================
st.markdown("---")
c1,c2,c3,c4 = st.columns(4)
c1.markdown(f'<div style="text-align:center;padding:12px;"><h4 style="color:#64748b;margin:0;">🕒 Sim Step</h4><div style="font-size:24px;font-weight:bold;color:#1e293b;">{st.session_state.step_count}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div style="text-align:center;padding:12px;"><h4 style="color:#64748b;margin:0;">✅ Completed</h4><div style="font-size:24px;font-weight:bold;color:#10b981;">{st.session_state.completed_count}</div></div>', unsafe_allow_html=True)
agvs_now = st.session_state.live_agvs
c3.markdown(f'<div style="text-align:center;padding:12px;"><h4 style="color:#64748b;margin:0;">🤖 Active / Total</h4><div style="font-size:24px;font-weight:bold;color:#3b82f6;">{sum(1 for a in agvs_now if not a["failed"])}/{len(agvs_now)}</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div style="text-align:center;padding:12px;"><h4 style="color:#64748b;margin:0;">📡 Sync</h4><div style="font-size:24px;font-weight:bold;color:#8b5cf6;">every 2s</div></div>', unsafe_allow_html=True)
