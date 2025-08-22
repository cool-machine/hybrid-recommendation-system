"""Streamlit front-end for the hybrid recommender

Run locally:
    streamlit run app.py --server.port 8501

Set environment variable RECO_API_URL to your Azure Function URL
(e.g. https://<func-name>.azurewebsites.net/api/HttpReco?code=<key>)
"""
from __future__ import annotations

import os
import pathlib
import random

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

API_URL = os.getenv("RECO_API_URL") or os.getenv("FUNCTION_URL") or ""
MAX_USER = 65_535  # upper bound of user IDs
RAND_COUNT = 12

st.set_page_config(page_title="Article Recommender Demo", page_icon="📰")

# Force cache refresh with timestamp
import time
cache_buster = int(time.time())
st.title("📰 Hybrid Recommender Showcase")
# Inject CSS/JS to style buttons as colored 3-D bubbles using components.html (injects into parent document)
components.html(r'''<script>
(function(){
  const css = `
  button.bubble{
    width:110px;height:110px;border-radius:50%;font-size:22px;font-weight:600;color:#000000;line-height:1;
    cursor:pointer;border:2px solid rgba(255,255,255,0.4);backdrop-filter:blur(4px);background:transparent;
    perspective:1000px;transform-style:preserve-3d;animation:float3d 18s ease-in-out infinite;transition:transform .25s;will-change:transform;
  }
  button.bubble:hover{transform:scale(1.15);}
  button.warm-bubble{
    background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
    border: 2px solid #357ABD !important;
    color: #ffffff !important;
    box-shadow:inset -2px -2px 8px rgba(255,255,255,0.3),inset 2px 2px 8px rgba(0,0,0,0.2),0 0 12px rgba(74,144,226,0.4);
  }
  button.cold-bubble{
    background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%) !important;
    border: 2px solid #C0392B !important;
    color: #ffffff !important;
    box-shadow:inset -2px -2px 8px rgba(255,255,255,0.3),inset 2px 2px 8px rgba(0,0,0,0.2),0 0 12px rgba(231,76,60,0.4);
  }
  @keyframes float3d{
    0%{transform:translate3d(0,0,0) rotateX(0deg) rotateY(0deg);}25%{transform:translate3d(18px,-25px,30px) rotateX(15deg) rotateY(-15deg);}50%{transform:translate3d(-22px,18px,-35px) rotateX(-12deg) rotateY(12deg);}75%{transform:translate3d(20px,12px,32px) rotateX(18deg) rotateY(-18deg);}100%{transform:translate3d(0,0,0) rotateX(0deg) rotateY(0deg);} }
  `;
  if(!parent.document.getElementById('bubble-css')){
    const style = parent.document.createElement('style');
    style.id = 'bubble-css';
    style.innerHTML = css;
    parent.document.head.appendChild(style);
  }
  function tag(){
    parent.document.querySelectorAll('button').forEach(btn=>{
      if(btn.classList.contains('bubble')) return;
      const txt = btn.innerText.trim();
      if(/^⭕️/.test(txt)) btn.classList.add('bubble','cold-bubble');
      else if(/^[0-9]+$/.test(txt)) btn.classList.add('bubble','warm-bubble');
    });
    // Fix text color based on current theme
    fixTextColors();
  }
  function fixTextColors(){
    // Force white text on all buttons (they now have colored backgrounds)
    parent.document.querySelectorAll('button').forEach(el=>{
      el.style.color = '#ffffff';
      el.style.fontWeight = '600';
    });
    // For inputs and selects, use adaptive colors based on theme
    const isDark = parent.window.matchMedia && parent.window.matchMedia('(prefers-color-scheme: dark)').matches;
    const inputTextColor = isDark ? '#ffffff' : '#000000';
    parent.document.querySelectorAll('input, select').forEach(el=>{
      el.style.color = inputTextColor;
    });
  }
  tag();
  const mo = new parent.MutationObserver(tag);
  mo.observe(parent.document.body,{childList:true,subtree:true});
  // Listen for theme changes
  if(parent.window.matchMedia){
    parent.window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', fixTextColors);
  }
})();
</script>''', height=0)


st.markdown(
    """
    <style>
.warm-section .stButton>button {
    background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
    border: 2px solid #357ABD !important;
    color: #ffffff !important;
    box-shadow: inset -2px -2px 8px rgba(255,255,255,0.3), inset 2px 2px 8px rgba(0,0,0,0.2), 0 0 12px rgba(74,144,226,0.4);
}

.cold-section .stButton>button {
    background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%) !important;
    border: 2px solid #C0392B !important;
    color: #ffffff !important;
    box-shadow: inset -2px -2px 8px rgba(255,255,255,0.3), inset 2px 2px 8px rgba(0,0,0,0.2), 0 0 12px rgba(231,76,60,0.4);
}

    /* bubble-style quick-pick buttons */
    .stButton>button {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: transparent;
        color: #000000;
        border: 2px solid #d0f0ff55;
        font-size: 24px;
        line-height: 1;
        cursor: pointer;
        perspective: 800px;
        transform-style: preserve-3d;
        animation: float3d 18s ease-in-out infinite;
        transition: transform 0.25s;
        will-change: transform;
    }
    .stButton>button:hover {
        transform: scale(1.12);
    }
    /* stagger animation so bubbles don't move in sync */
    .stButton>button:nth-of-type(2n) { animation-delay: 3s; animation-direction: reverse; }
    .stButton>button:nth-of-type(3n) { animation-delay: 6s; animation-direction: alternate; }
    .stButton>button:nth-of-type(4n) { animation-delay: 9s; animation-duration: 24s; }
    /* Force proper text color for buttons (always white on colored backgrounds) */
button.bubble, .stButton>button {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* For inputs and selects, use theme-appropriate colors */
@media (prefers-color-scheme: dark) {
    .stNumberInput input, .stSelectbox select, .stTextInput input {
        color: #ffffff !important;
    }
}
@media (prefers-color-scheme: light) {
    .stNumberInput input, .stSelectbox select, .stTextInput input {
        color: #000000 !important;
    }
}
/* Auto-detect theme and apply appropriate colors */
[data-theme="dark"] button.bubble, [data-theme="dark"] .stButton>button, 
html[data-theme="dark"] button.bubble, html[data-theme="dark"] .stButton>button {
    color: #ffffff !important;
}
[data-theme="light"] button.bubble, [data-theme="light"] .stButton>button,
html[data-theme="light"] button.bubble, html[data-theme="light"] .stButton>button {
    color: #000000 !important;
}
@keyframes float3d {
        0%   {transform: translate3d(0px, 0px, 0px) rotateX(0deg) rotateY(0deg);}    
        20%  {transform: translate3d(15px, -20px, 30px) rotateX(6deg)  rotateY(-6deg);}   
        40%  {transform: translate3d(-18px, 12px, -40px) rotateX(-8deg) rotateY(4deg);}   
        60%  {transform: translate3d(22px, 8px, 25px)  rotateX(10deg) rotateY(-8deg);}    
        80%  {transform: translate3d(-12px, -14px, -20px) rotateX(-4deg) rotateY(6deg);} 
        100% {transform: translate3d(0px, 0px, 0px) rotateX(0deg) rotateY(0deg);}    
    }</style>
<!-- FINAL OVERRIDE FOR BUBBLES -->
<style id='bubble-final'>
.warm .stButton>button{
    background: radial-gradient(circle at 30% 35%, rgba(120,170,255,0.70) 0%, rgba(120,170,255,0.35) 55%, rgba(120,170,255,0.15) 100%) !important;
    border-color: rgba(120,170,255,0.65) !important;
}
.cold .stButton>button{
    background: radial-gradient(circle at 30% 35%, rgba(240,90,90,0.70) 0%, rgba(240,90,90,0.35) 55%, rgba(240,90,90,0.15) 100%) !important;
    border-color: rgba(240,90,90,0.65) !important;
}
/* stronger 3D tilt */
@keyframes float3d{
  0%{transform:translate3d(0,0,0) rotateX(0deg) rotateY(0deg);} 
  25%{transform:translate3d(20px,-30px,30px) rotateX(18deg) rotateY(-18deg);} 
  50%{transform:translate3d(-25px,20px,-40px) rotateX(-15deg) rotateY(15deg);} 
  75%{transform:translate3d(22px,15px,35px) rotateX(20deg) rotateY(-20deg);} 
  100%{transform:translate3d(0,0,0) rotateX(0deg) rotateY(0deg);} 
}
</style>
    """,
    unsafe_allow_html=True,
)
# --- override CSS for 3-D transparent bubbles ---
st.markdown(
    """
    <style>
    /* base bubble */
    .stButton>button{
        width:110px;height:110px;border-radius:50%;font-size:22px;color:#000000;font-weight:600;
        line-height:1;cursor:pointer;border:2px solid rgba(255,255,255,0.35);
        background:transparent;backdrop-filter:blur(6px);
        perspective:1000px;transform-style:preserve-3d;
        animation:float3d 18s ease-in-out infinite;transition:transform .25s;will-change:transform;
    }
    .stButton>button:hover{transform:scale(1.15);}
    /* warm - solid blue background with white text */
    .warm .stButton>button{
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
        border: 2px solid #357ABD !important;
        color: #ffffff !important;
        box-shadow: inset -2px -2px 8px rgba(255,255,255,0.3), inset 2px 2px 8px rgba(0,0,0,0.2), 0 0 12px rgba(74,144,226,0.4);
    }
    /* cold - solid red background with white text */
    .cold .stButton>button{
        background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%) !important;
        border: 2px solid #C0392B !important;
        color: #ffffff !important;
        box-shadow: inset -2px -2px 8px rgba(255,255,255,0.3), inset 2px 2px 8px rgba(0,0,0,0.2), 0 0 12px rgba(231,76,60,0.4);
    }
    @keyframes float3d{
        0%{transform:translate3d(0,0,0)rotateX(0deg)rotateY(0deg);}
        25%{transform:translate3d(15px,-25px,25px)rotateX(8deg)rotateY(-8deg);}
        50%{transform:translate3d(-20px,15px,-35px)rotateX(-6deg)rotateY(6deg);}
        75%{transform:translate3d(18px,10px,30px)rotateX(10deg)rotateY(-10deg);}
        100%{transform:translate3d(0,0,0)rotateX(0deg)rotateY(0deg);}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if not API_URL:
    st.warning("Set RECO_API_URL as env var to enable backend calls.")

# --- pick list of random users each session ---------------------------------
# warm users (with ground-truth)
GT_USERS: list[int]
try:
    npy_path = pathlib.Path(__file__).parent.parent / "functions_reco" / "artifacts" / "gt_users.npy"
    GT_USERS = np.load(npy_path).astype(int).tolist() if npy_path.exists() else []
except Exception:
    GT_USERS = []

# fallback: if still empty, fill with a range so that bubbles show up in demo mode
if not GT_USERS:
    GT_USERS = list(range(100))  # first 100 user IDs as generic warm users

# cold users (no history)
COLD_USERS: list[int]
try:
    cold_path = pathlib.Path(__file__).parent.parent / "functions_reco" / "artifacts" / "cold_users.npy"
    COLD_USERS = np.load(cold_path).astype(int).tolist() if cold_path.exists() else []
except Exception:
    COLD_USERS = []
# fallback demo pool
if not COLD_USERS:
    COLD_USERS = list(range(1000, 1100))

if "sample_users" not in st.session_state:
    st.session_state.sample_users = random.sample(GT_USERS, min(RAND_COUNT, len(GT_USERS))) if GT_USERS else []
if "sample_cold" not in st.session_state:
    st.session_state.sample_cold = random.sample(COLD_USERS, min(RAND_COUNT, len(COLD_USERS))) if COLD_USERS else []
if "selected_uid" not in st.session_state:
    st.session_state.selected_uid = 0

st.markdown("<div class='warm'>", unsafe_allow_html=True)
st.markdown("### 🔥 Warm users (have ground-truth)")
clicked_user = None
NUM_COLS = 4  # bubbles per row
# --- warm user bubbles -------------------------------------------------------
for i, uid in enumerate(st.session_state.sample_users[:RAND_COUNT]):
    if i % NUM_COLS == 0:
        cols = st.columns(NUM_COLS)
    col = cols[i % NUM_COLS]
    if col.button(str(uid), key=f"warm_{uid}"):
        st.session_state.selected_uid = uid
        clicked_user = uid

# close warm wrapper
st.markdown("</div>", unsafe_allow_html=True)
# --- cold user bubbles -------------------------------------------------------
st.markdown("<div class='cold'>", unsafe_allow_html=True)
st.markdown("### 🔴 Cold users (no history)")
for i, uid in enumerate(st.session_state.sample_cold[:RAND_COUNT]):
    if i % NUM_COLS == 0:
        cols = st.columns(NUM_COLS)
    col = cols[i % NUM_COLS]
    if col.button(f"⭕️ {uid}", key=f"cold_{uid}"):
        st.session_state.selected_uid = uid
        clicked_user = uid

st.markdown("### Or enter a user ID")
# close cold wrapper
st.markdown("</div>", unsafe_allow_html=True)

manual_id = st.number_input("User ID", min_value=0, max_value=MAX_USER, step=1,
                                value=st.session_state.selected_uid, key="manual_uid")
# update session value from manual entry
st.session_state.selected_uid = int(manual_id)
selected_uid = st.session_state.selected_uid

k = st.selectbox("How many recommendations?", [5, 10, 20], index=1)

# --- contextual fields for cold-start ---------------------------------------
with st.expander("Context (for cold users)"):
    device_group = st.selectbox("Device group", {"mobile":0,"desktop":1,"tablet":2}, index=1, key="dev_grp")
    os_id        = st.selectbox("OS", {"Android":0,"iOS":1,"Windows":2,"macOS":3,"Linux":4,"Other":5}, index=3, key="os_id")
    country      = st.text_input("Country code (ISO 2)", "US", max_chars=2)

# Add aggressive CSS override to ensure button visibility
st.markdown("""
<style>
/* EMERGENCY FIX - Override all button styles */
.stButton > button, button {
    background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: 3px solid #357ABD !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5) !important;
}

/* Cold user buttons (with ⭕) */
[data-testid*="cold"] .stButton > button,
.cold .stButton > button {
    background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%) !important;
    border: 3px solid #C0392B !important;
}

/* Force ALL buttons to have visible text */
button, .stButton > button {
    color: #ffffff !important;
    font-weight: 700 !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    background: #4A90E2 !important;
    border: 2px solid #357ABD !important;
    min-height: 50px !important;
}
</style>
""", unsafe_allow_html=True)

if st.button("🔍 Get recommendations"):
    if not API_URL:
        st.error("API URL not configured.")
    else:
        with st.spinner("Calling backend …"):
            try:
                payload = {"user_id": selected_uid, "k": k, "env": {"device": device_group, "os": os_id, "country": country.upper()}}
                resp = requests.post(API_URL, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                st.error(f"Request failed: {e}")
            else:
                st.success("Recommendations received!")
                user_type = "First-time user" if selected_uid in COLD_USERS else "Returning user"
                st.write(f"**User:** {selected_uid}  ·  *{user_type}*")
                if data.get('ground_truth') is not None:
                    st.write(f"**Ground-truth click:** {data.get('ground_truth')}")
                st.markdown("#### Top items")
                for rank, item in enumerate(data.get("recommendations", []), start=1):
                    st.write(f"{rank}. Article {item}")
