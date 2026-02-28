import streamlit as st
import pandas as pd
from collections import Counter
import datetime

# ==========================================
# 🧠 THE MASTER PATTERN REPOSITORY
# ==========================================

# ENGINE 1: EXACT DETERMINISTIC RULES
EXACT_RULES = {
    "SSSBSBSBBS": "B",
    "SSBBSBSSBBB": "S",
    "GGRRRGRRRRRG": "G",
    "BRBRBRBGSGSR": "BG",
    "9955": "6",
    "BRSRBGBGSRSRSG": "BG",
    "SGBGSGBRBRBGSGSR": "SG"
}

# ENGINE 1: REPEATING CYCLE RULES (MODEL 3)
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
    "011010000011": "R",
    "011111101111": "B",
    "000001100101": "R",
    "010000100000": "R"
}

# ==========================================
# ⚙️ CORE LOGIC FUNCTIONS
# ==========================================

def get_structure(seq):
    mapping = {}
    return "".join([mapping.setdefault(x, str(len(mapping))) for x in seq])

def get_predictions(history):
    p1, m1, p2, m2 = None, None, None, None
    
    # Engine 1 Search
    for length in [12, 11, 10, 8, 7, 6, 4]:
        if len(history) < length: continue
        chunk = "".join(history[-length:])
        
        if chunk in EXACT_RULES:
            p1, m1 = EXACT_RULES[chunk], "Engine 1 (Deterministic)"
            break
        if chunk in CYCLE_RULES:
            cycle = CYCLE_RULES[chunk]
            count = st.session_state.cycle_counts.get(chunk, 0)
            p1, m1 = cycle[count % len(cycle)], f"Engine 1 (Cycle Pos: {count % len(cycle)})"
            break

    # Engine 2 Search
    if len(history) >= 12:
        struct = get_structure(history[-12:])
        if struct in STRUCTURAL_RULES:
            p2, m2 = STRUCTURAL_RULES[struct], "Engine 2 (Structure AI)"
            
    return p1, m1, p2, m2

# ==========================================
# 📱 APP INTERFACE (STREAMLIT)
# ==========================================

st.set_page_config(page_title="2-Engg Master AI", layout="wide")
st.title("🛡️ 2-Engine Pattern Master App")

if 'history' not in st.session_state: st.session_state.history = []
if 'log' not in st.session_state: st.session_state.log = []
if 'cycle_counts' not in st.session_state: st.session_state.cycle_counts = {}

# Sidebar Reset
if st.sidebar.button("Reset Session"):
    st.session_state.history, st.session_state.log, st.session_state.cycle_counts = [], [], {}
    st.rerun()

# 1. Inputs
st.subheader("Add Result")
c1, c2, c3, c4 = st.columns(4)

def record(val):
    p1, m1, p2, m2 = get_predictions(st.session_state.history)
    
    # Update Cycle Memory
    for length in [10, 11]:
        if len(st.session_state.history) >= length:
            chunk = "".join(st.session_state.history[-length:])
            if chunk in CYCLE_RULES:
                st.session_state.cycle_counts[chunk] = st.session_state.cycle_counts.get(chunk, 0) + 1

    st.session_state.log.append({
        "Time": datetime.datetime.now().strftime("%H:%M:%S"),
        "Entered": val,
        "Eng1_Pred": p1 if p1 else "-",
        "Eng2_Pred": p2 if p2 else "-",
        "Result": "✅" if (val == p1 or val == p2) else "❌" if (p1 or p2) else "-"
    })
    st.session_state.history.append(val)

if c1.button("SR", use_container_width=True): record("SR")
if c2.button("SG", use_container_width=True): record("SG")
if c3.button("BR", use_container_width=True): record("BR")
if c4.button("BG", use_container_width=True): record("BG")

# 2. Next Predictions
st.divider()
np1, msg1, np2, msg2 = get_predictions(st.session_state.history)

res1, res2 = st.columns(2)
res1.metric("Engine 1 (Tracker)", str(np1) if np1 else "---", msg1)
res2.metric("Engine 2 (Subber AI)", str(np2) if np2 else "---", msg2)

# 3. Log and Download
st.subheader("📊 Streak Tracking & History")
if st.session_state.log:
    log_df = pd.DataFrame(st.session_state.log).iloc[::-1]
    st.table(log_df)
    csv = pd.DataFrame(st.session_state.log).to_csv(index=False)
    st.download_button("📥 Download Streak Result", csv, "streak_tracking.csv", "text/csv")
