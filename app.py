import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# ==========================================
# 🧠 ALL YOUR 100% PATTERNS (HARDCODED)
# ==========================================

# ENGINE 1: EXACT MATCHES
EXACT_RULES = {
    "SSSBSBSBBS": "B", "SSBBSBSSBBB": "S", "GGRRRGRRRRRG": "G",
    "BRBRBRBGSGSR": "BG", "9955": "6", "BRSRBGBGSRSRSG": "BG",
    "SGBGSGBRBRBGSGSR": "SG"
}

# ENGINE 1: REPEATING CYCLES (MODEL 3)
CYCLE_RULES = {
    "GGGRRGGGGG": ["G", "G", "G", "G", "G", "G", "R", "R"],
    "GRRRGGGGRR": ["R", "R", "G", "G", "G", "G", "G", "G"],
    "GRRGGGRRRR": ["R", "G", "G", "G", "R", "G", "R"],
    "BBBSBSSSBBS": ["B", "B", "B", "B", "B", "S"],
    "SBSSSBBBSS": ["B", "B", "S", "B", "S", "B", "B"],
    "RGRGRGGGRG": ["R", "R", "G", "R", "G", "G"]
}

# ENGINE 2: STRUCTURAL RULES (MODEL 2)
STRUCTURAL_RULES = {
    "011010000011": "R", "011111101111": "B",
    "000001100101": "R", "010000100000": "R"
}

# ==========================================
# ⚙️ ENGINE LOGIC
# ==========================================

def get_structure(seq):
    m = {}
    return "".join([m.setdefault(x, str(len(m))) for x in seq])

def get_predictions(history):
    p1, m1, p2, m2 = None, None, None, None
    
    # Engine 1: Exact & Cycles
    for L in [12, 11, 10, 8, 7, 6, 4]:
        if len(history) < L: continue
        chunk = "".join(history[-L:])
        if chunk in EXACT_RULES:
            p1, m1 = EXACT_RULES[chunk], f"Eng 1: Deterministic ({L}d)"
            break
        if chunk in CYCLE_RULES:
            cycle = CYCLE_RULES[chunk]
            count = st.session_state.get(f"c_{chunk}", 0)
            p1, m1 = cycle[count % len(cycle)], f"Eng 1: Cycle (Pos {count % len(cycle)})"
            break

    # Engine 2: Subber AI Structure
    if len(history) >= 12:
        struct = get_structure(history[-12:])
        if struct in STRUCTURAL_RULES:
            p2, m2 = STRUCTURAL_RULES[struct], "Eng 2: Subber Structural AI"
            
    return p1, m1, p2, m2

# ==========================================
# 📱 APP INTERFACE
# ==========================================

st.set_page_config(page_title="Pattern Master AI", layout="wide")
st.title("🛡️ Dual-Engine Pattern Tracker")

if 'history' not in st.session_state: st.session_state.history = []
if 'log' not in st.session_state: st.session_state.log = []

# Sidebar
if st.sidebar.button("🗑️ Reset All Game Data"):
    st.session_state.history = []
    st.session_state.log = []
    st.rerun()

# 1. Inputs
st.subheader("Add Result")
cols = st.columns(4)
opts = ["SR", "SG", "BR", "BG"]

def record(val):
    p1, m1, p2, m2 = get_predictions(st.session_state.history)
    
    # Update Cycle Counters
    for L in [10, 11]:
        if len(st.session_state.history) >= L:
            chunk = "".join(st.session_state.history[-L:])
            if chunk in CYCLE_RULES:
                key = f"c_{chunk}"
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

# 2. Next Predictions Dashboard
st.divider()
np1, msg1, np2, msg2 = get_predictions(st.session_state.history)


c1, c2 = st.columns(2)
c1.metric("Engine 1 (Tracker)", str(np1) if np1 else "---", msg1)
c2.metric("Engine 2 (Subber AI)", str(np2) if np2 else "---", msg2)

# 3. Live Tracking Log
st.subheader("📊 Streak Log")
if st.session_state.log:
    df = pd.DataFrame(st.session_state.log).iloc[::-1]
    st.table(df)
    st.download_button("📥 Download Results (CSV)", df.to_csv(index=False), "streak.csv")
