import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# ==========================================
# 🧠 ENGINE DATABASE (HARDCODED)
# ==========================================

# ENGINE 1: EXACT MATCHES & CYCLES
EXACT_LOGIC = {
    "SSSBSBSBBS": "B", "SSBBSBSSBBB": "S", "GGRRRGRRRRRG": "G",
    "BRBRBRBGSGSR": "BG", "9955": "6", "BRSRBGBGSRSRSG": "BG",
    "SGBGSGBRBRBGSGSR": "SG"
}

CYCLE_LOGIC = {
    "GGGRRGGGGG": ["G", "G", "G", "G", "G", "G", "R", "R"],
    "GRRRGGGGRR": ["R", "R", "G", "G", "G", "G", "G", "G"],
    "GRRGGGRRRR": ["R", "G", "G", "G", "R", "G", "R"],
    "BBBSBSSSBBS": ["B", "B", "B", "B", "B", "S"],
    "SBSSSBBBSS": ["B", "B", "S", "B", "S", "B", "B"],
    "RGRGRGGGRG": ["R", "R", "G", "R", "G", "G"]
}

# ENGINE 2: STRUCTURAL AI (MODEL 2)
STRUCTURAL_LOGIC = {
    "011010000011": "R", "011111101111": "B",
    "000001100101": "R", "010000100000": "R"
}

# ==========================================
# ⚙️ SYSTEM UNDERSTANDING & FORMAT
# ==========================================

def get_structure(seq):
    """Converts patterns to relative numbers (0, 1, 2)"""
    m = {}
    return "".join([m.setdefault(x, str(len(m))) for x in seq])

def get_predictions(history):
    p1, m1, p2, m2 = None, None, None, None
    
    # Engine 1: Tracker (Matches & Cycles)
    for L in [12, 11, 10, 8, 7, 6, 4]:
        if len(history) < L: continue
        chunk = "".join(history[-L:])
        if chunk in EXACT_LOGIC:
            p1, m1 = EXACT_LOGIC[chunk], f"Eng 1: Exact Match ({L}d)"
            break
        if chunk in CYCLE_LOGIC:
            cycle = CYCLE_LOGIC[chunk]
            count = st.session_state.get(f"count_{chunk}", 0)
            p1, m1 = cycle[count % len(cycle)], f"Eng 1: Cycle (Pos {count % len(cycle)})"
            break

    # Engine 2: Subber AI (Structure)
    if len(history) >= 12:
        struct = get_structure(history[-12:])
        if struct in STRUCTURAL_LOGIC:
            p2, m2 = STRUCTURAL_LOGIC[struct], "Eng 2: Structural AI"
            
    return p1, m1, p2, m2

# ==========================================
# 📱 GAME INTERFACE
# ==========================================

st.set_page_config(page_title="2-Engg Master", layout="wide")
st.title("🛡️ 2-Engg Pattern Track & Subber AI")

if 'history' not in st.session_state: st.session_state.history = []
if 'log' not in st.session_state: st.session_state.log = []

# Sidebar
if st.sidebar.button("Reset Game"):
    st.session_state.history = []
    st.session_state.log = []
    st.rerun()

# Inputs
st.subheader("Input Result")
cols = st.columns(4)
opts = ["SR", "SG", "BR", "BG"]

def record(val):
    p1, m1, p2, m2 = get_predictions(st.session_state.history)
    
    # Update Cycle Counters
    for L in [10, 11]:
        if len(st.session_state.history) >= L:
            chunk = "".join(st.session_state.history[-L:])
            if chunk in CYCLE_LOGIC:
                key = f"count_{chunk}"
                st.session_state[key] = st.session_state.get(key, 0) + 1

    st.session_state.log.append({
        "Time": datetime.datetime.now().strftime("%H:%M:%S"),
        "Input": val,
        "Eng1_Pred": p1 if p1 else "-",
        "Eng2_Pred": p2 if p2 else "-",
        "Status": "✅" if (val == p1 or val == p2) else "❌" if (p1 or p2) else "-"
    })
    st.session_state.history.append(val)

for i, opt in enumerate(opts):
    if cols[i].button(f"PUSH {opt}", use_container_width=True): record(opt)

# Next Predictions
st.divider()
np1, msg1, np2, msg2 = get_predictions(st.session_state.history)

c1, c2 = st.columns(2)
c1.metric("Engine 1 (Tracker)", str(np1) if np1 else "Searching...", msg1)
c2.metric("Engine 2 (Subber AI)", str(np2) if np2 else "Analyzing...", msg2)

# Tracking Table
st.subheader("📊 Streak Log & Download")
if st.session_state.log:
    df = pd.DataFrame(st.session_state.log).iloc[::-1]
    st.table(df)
    st.download_button("📥 Download streak_tracking.csv", df.to_csv(index=False), "streak.csv")
